import hashlib
import pandas as pd
import numpy as np
from src.logger import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = [
    "hotel",
    "is_canceled",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "country",
    "market_segment",
    "distribution_channel",
    "is_repeated_guest",
    "previous_cancellations",
    "booking_changes",
    "deposit_type",
    "customer_type",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "reservation_status",
    "reservation_status_date",
]

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def compute_canonical_base_hash(row) -> str:
    """
    Computes a SHA256 base hash from canonical string of all transformed source attributes available
    before booking_id generation.
    """
    canonical_parts = [
        str(row.get(c, "")).strip() for c in REQUIRED_COLUMNS if c in row
    ]
    canonical_string = "|".join(canonical_parts)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()[:20].upper()

def transform_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw hotel booking DataFrame according to business logic rules:
    - Purges exact duplicates
    - Normalizes casing and trims string whitespace
    - Coerces numerical fields and parses arrival_date and reservation_status_date
    - Computes total_nights, total_guests
    - Computes booking_value = adr * total_nights
    - Computes estimated_revenue = booking_value if is_canceled == 0 else 0
    - Generates deterministic SHA256-based surrogate booking_id with sequence suffix

    :param raw_df: Input raw pandas DataFrame.
    :return: Transformed pandas DataFrame ready for validation.
    """
    logger.info("====================================")
    logger.info("STAGE 2: TRANSFORMATION STARTED")
    logger.info("====================================")

    df = raw_df.copy()
    initial_rows = len(df)
    logger.info(f"Input row count for transformation: {initial_rows}")

    # 1. Keep required columns only
    existing_cols = [c for c in REQUIRED_COLUMNS if c in df.columns]
    df = df[existing_cols]

    # 2. Remove exact duplicate records
    dedup_df = df.drop_duplicates()
    duplicates_removed = len(df) - len(dedup_df)
    df = dedup_df.reset_index(drop=True)
    logger.info(f"Removed {duplicates_removed} exact duplicate records. Remaining: {len(df)}")

    # 3. Trim whitespace from string columns
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        df[c] = df[c].replace({"nan": np.nan, "None": np.nan, "null": np.nan, "": np.nan})

    # 4. Standardize text casing
    if "country" in df.columns:
        df["country"] = df["country"].str.upper()
    
    title_case_cols = ["hotel", "market_segment", "customer_type", "reservation_status", "deposit_type", "distribution_channel"]
    for c in title_case_cols:
        if c in df.columns:
            df[c] = df[c].str.title()

    # 5 & 6. Convert numeric columns safely
    numeric_cols = [
        "is_canceled", "lead_time", "arrival_date_year", "arrival_date_day_of_month",
        "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children", "babies",
        "is_repeated_guest", "previous_cancellations", "booking_changes", "adr",
        "required_car_parking_spaces", "total_of_special_requests"
    ]

    if "children" in df.columns:
        df["children"] = df["children"].fillna(0)

    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 7. Build arrival_date column
    def parse_arrival_date(row):
        try:
            year = int(row["arrival_date_year"])
            month_val = str(row["arrival_date_month"]).strip().lower()
            day = int(row["arrival_date_day_of_month"])

            if month_val.isdigit():
                month = int(month_val)
            else:
                month = MONTH_MAP.get(month_val, np.nan)

            if pd.isna(month):
                return pd.NaT

            return pd.Timestamp(year=year, month=int(month), day=day).date()
        except Exception:
            return pd.NaT

    df["arrival_date"] = df.apply(parse_arrival_date, axis=1)
    df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce").dt.date

    # 8. Convert reservation_status_date to datetime
    if "reservation_status_date" in df.columns:
        df["reservation_status_date"] = pd.to_datetime(df["reservation_status_date"], errors="coerce").dt.date

    # 9. Calculate total_nights = stays_in_weekend_nights + stays_in_week_nights
    df["stays_in_weekend_nights"] = df["stays_in_weekend_nights"].fillna(0)
    df["stays_in_week_nights"] = df["stays_in_week_nights"].fillna(0)
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]

    # 10. Calculate total_guests = adults + children + babies
    df["adults"] = df["adults"].fillna(0)
    df["children"] = df["children"].fillna(0)
    df["babies"] = df["babies"].fillna(0)
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]

    # 11. Calculate booking_value and estimated_revenue
    df["adr"] = df["adr"].fillna(0.0)
    # booking_value: Potential monetary value regardless of cancellation
    df["booking_value"] = (df["adr"] * df["total_nights"]).clip(lower=0.0)
    # estimated_revenue: Realized revenue only for non-canceled bookings (0 if canceled)
    df["estimated_revenue"] = np.where(df["is_canceled"] == 0, df["booking_value"], 0.0)

    # 12. Generate deterministic SHA256-based surrogate booking_id with sequence suffix
    base_hashes = [compute_canonical_base_hash(row) for _, row in df.iterrows()]
    df["_base_hash"] = base_hashes
    seq_nums = df.groupby("_base_hash").cumcount() + 1
    
    booking_ids = [
        f"HB-{h}-{s:02d}" for h, s in zip(base_hashes, seq_nums)
    ]
    df.insert(0, "booking_id", booking_ids)
    df.drop(columns=["_base_hash"], inplace=True)

    if not df["booking_id"].is_unique:
        raise ValueError("Non-unique booking_id values produced during transformation!")

    logger.info(f"Transformation completed. Final Transformed DataFrame Shape: {df.shape}")
    return df

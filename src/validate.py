from typing import Tuple
import pandas as pd
import numpy as np
from src.logger import get_logger

logger = get_logger(__name__)

def validate_records(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validates hotel booking records against business logic rules.
    Splits records into valid and rejected DataFrames.
    Multiple validation failures are concatenated into rejection_reason separated by semicolons.

    :param df: Transformed DataFrame.
    :return: Tuple (valid_df, rejected_df).
    """
    logger.info("====================================")
    logger.info("STAGE 3: VALIDATION STARTED")
    logger.info("====================================")

    records = df.to_dict(orient="records")
    valid_list = []
    rejected_list = []

    for row in records:
        reasons = []

        # 1. Null / Missing field checks
        if pd.isna(row.get("booking_id")) or str(row.get("booking_id")).strip() in ["", "nan", "None"]:
            reasons.append("missing booking_id")

        if pd.isna(row.get("hotel")) or str(row.get("hotel")).strip() in ["", "nan", "None"]:
            reasons.append("missing hotel")

        if pd.isna(row.get("country")) or str(row.get("country")).strip() in ["", "nan", "None"]:
            reasons.append("missing country")

        if pd.isna(row.get("arrival_date")):
            reasons.append("invalid arrival_date")

        if pd.isna(row.get("reservation_status_date")):
            reasons.append("invalid reservation_status_date")

        # 2. Value boundary & integrity checks
        adults = row.get("adults")
        if pd.isna(adults) or adults < 1:
            reasons.append("adults must be >= 1")

        children = row.get("children")
        if pd.isna(children) or children < 0:
            reasons.append("children must be >= 0")

        babies = row.get("babies")
        if pd.isna(babies) or babies < 0:
            reasons.append("babies must be >= 0")

        total_guests = row.get("total_guests")
        if pd.isna(total_guests) or total_guests < 1:
            reasons.append("total_guests must be >= 1")

        lead_time = row.get("lead_time")
        if pd.isna(lead_time) or lead_time < 0:
            reasons.append("lead_time must be >= 0")

        weekend_nights = row.get("stays_in_weekend_nights")
        if pd.isna(weekend_nights) or weekend_nights < 0:
            reasons.append("stays_in_weekend_nights must be >= 0")

        week_nights = row.get("stays_in_week_nights")
        if pd.isna(week_nights) or week_nights < 0:
            reasons.append("stays_in_week_nights must be >= 0")

        total_nights = row.get("total_nights")
        if pd.isna(total_nights) or total_nights < 0:
            reasons.append("total_nights must be >= 0")

        adr = row.get("adr")
        if pd.isna(adr) or adr < 0:
            reasons.append("negative adr")

        booking_val = row.get("booking_value")
        if pd.isna(booking_val) or booking_val < 0:
            reasons.append("negative booking_value")

        est_rev = row.get("estimated_revenue")
        if pd.isna(est_rev) or est_rev < 0:
            reasons.append("negative estimated_revenue")

        is_canceled = row.get("is_canceled")
        if pd.isna(is_canceled) or is_canceled not in [0, 1]:
            reasons.append("is_canceled must be 0 or 1")

        is_repeated_guest = row.get("is_repeated_guest")
        if pd.isna(is_repeated_guest) or is_repeated_guest not in [0, 1]:
            reasons.append("is_repeated_guest must be 0 or 1")

        prev_cancellations = row.get("previous_cancellations")
        if pd.isna(prev_cancellations) or prev_cancellations < 0:
            reasons.append("previous_cancellations must be >= 0")

        booking_changes = row.get("booking_changes")
        if pd.isna(booking_changes) or booking_changes < 0:
            reasons.append("booking_changes must be >= 0")

        parking = row.get("required_car_parking_spaces")
        if pd.isna(parking) or parking < 0:
            reasons.append("required_car_parking_spaces must be >= 0")

        special_requests = row.get("total_of_special_requests")
        if pd.isna(special_requests) or special_requests < 0:
            reasons.append("total_of_special_requests must be >= 0")

        if reasons:
            row["rejection_reason"] = "; ".join(reasons)
            rejected_list.append(row)
        else:
            valid_list.append(row)

    valid_df = pd.DataFrame(valid_list) if valid_list else pd.DataFrame(columns=df.columns)
    rejected_df = pd.DataFrame(rejected_list) if rejected_list else pd.DataFrame(columns=list(df.columns) + ["rejection_reason"])

    total_records = len(df)
    valid_count = len(valid_df)
    rejected_count = len(rejected_df)
    rejection_pct = (rejected_count / total_records * 100) if total_records > 0 else 0.0

    logger.info("Validation Summary:")
    logger.info(f"  - Total Transformed Records: {total_records}")
    logger.info(f"  - Valid Records:             {valid_count}")
    logger.info(f"  - Rejected Records:          {rejected_count}")
    logger.info(f"  - Rejection Rate:            {rejection_pct:.2f}%")

    return valid_df, rejected_df

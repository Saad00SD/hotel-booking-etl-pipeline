import pytest
import pandas as pd
import numpy as np

from src.transform import transform_data, compute_canonical_base_hash

def sample_raw_dataframe():
    """
    Constructs a sample raw DataFrame for transformation testing.
    """
    data = [
        # Row 0: Non-canceled booking
        {
            "hotel": " resort hotel ",
            "is_canceled": 0,
            "lead_time": 342,
            "arrival_date_year": 2015,
            "arrival_date_month": "July",
            "arrival_date_day_of_month": 1,
            "stays_in_weekend_nights": 0,
            "stays_in_week_nights": 2,
            "adults": 2,
            "children": 1.0,
            "babies": 0,
            "country": " prt ",
            "market_segment": " direct ",
            "distribution_channel": "Direct",
            "is_repeated_guest": 0,
            "previous_cancellations": 0,
            "booking_changes": 0,
            "deposit_type": " no deposit ",
            "customer_type": " transient ",
            "adr": 100.0,
            "required_car_parking_spaces": 0,
            "total_of_special_requests": 1,
            "reservation_status": " check-out ",
            "reservation_status_date": "2015-07-03",
        },
        # Row 1: Duplicate record of row 0 to test deduplication
        {
            "hotel": " resort hotel ",
            "is_canceled": 0,
            "lead_time": 342,
            "arrival_date_year": 2015,
            "arrival_date_month": "July",
            "arrival_date_day_of_month": 1,
            "stays_in_weekend_nights": 0,
            "stays_in_week_nights": 2,
            "adults": 2,
            "children": 1.0,
            "babies": 0,
            "country": " prt ",
            "market_segment": " direct ",
            "distribution_channel": "Direct",
            "is_repeated_guest": 0,
            "previous_cancellations": 0,
            "booking_changes": 0,
            "deposit_type": " no deposit ",
            "customer_type": " transient ",
            "adr": 100.0,
            "required_car_parking_spaces": 0,
            "total_of_special_requests": 1,
            "reservation_status": " check-out ",
            "reservation_status_date": "2015-07-03",
        },
        # Row 2: Canceled booking
        {
            "hotel": "city hotel",
            "is_canceled": 1,
            "lead_time": 45,
            "arrival_date_year": 2016,
            "arrival_date_month": "August",
            "arrival_date_day_of_month": 15,
            "stays_in_weekend_nights": 1,
            "stays_in_week_nights": 3,
            "adults": 1,
            "children": np.nan,
            "babies": 0,
            "country": "gbr",
            "market_segment": "online ta",
            "distribution_channel": "TA/TO",
            "is_repeated_guest": 0,
            "previous_cancellations": 1,
            "booking_changes": 0,
            "deposit_type": "non refund",
            "customer_type": "contract",
            "adr": 85.50,
            "required_car_parking_spaces": 0,
            "total_of_special_requests": 0,
            "reservation_status": "canceled",
            "reservation_status_date": "2016-08-10",
        }
    ]
    return pd.DataFrame(data)

def test_duplicate_removal():
    raw_df = sample_raw_dataframe()
    assert len(raw_df) == 3
    transformed = transform_data(raw_df)
    assert len(transformed) == 2

def test_casing_normalization():
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row0 = transformed.iloc[0]

    assert row0["country"] == "PRT"
    assert row0["hotel"] == "Resort Hotel"
    assert row0["market_segment"] == "Direct"
    assert row0["customer_type"] == "Transient"
    assert row0["deposit_type"] == "No Deposit"
    assert row0["reservation_status"] == "Check-Out"

def test_arrival_date_creation():
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row0 = transformed.iloc[0]
    row1 = transformed.iloc[1]

    assert str(row0["arrival_date"]) == "2015-07-01"
    assert str(row1["arrival_date"]) == "2016-08-15"

def test_total_nights_calculation():
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row0 = transformed.iloc[0]  # 0 weekend + 2 week
    row1 = transformed.iloc[1]  # 1 weekend + 3 week

    assert row0["total_nights"] == 2
    assert row1["total_nights"] == 4

def test_total_guests_calculation():
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row0 = transformed.iloc[0]  # 2 adults + 1 children + 0 babies
    row1 = transformed.iloc[1]  # 1 adult + 0 children + 0 babies

    assert row0["total_guests"] == 3
    assert row1["total_guests"] == 1

def test_non_canceled_booking_revenue():
    """Non-canceled booking: estimated_revenue == booking_value."""
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row0 = transformed.iloc[0]

    assert row0["is_canceled"] == 0
    assert row0["booking_value"] == 200.0  # adr 100 * 2 nights
    assert row0["estimated_revenue"] == 200.0
    assert row0["estimated_revenue"] == row0["booking_value"]

def test_canceled_booking_revenue():
    """Canceled booking: booking_value > 0 but estimated_revenue == 0."""
    raw_df = sample_raw_dataframe()
    transformed = transform_data(raw_df)
    row1 = transformed.iloc[1]  # is_canceled = 1

    assert row1["is_canceled"] == 1
    assert row1["booking_value"] == 342.0  # adr 85.50 * 4 nights
    assert row1["estimated_revenue"] == 0.0

def test_deterministic_booking_id_rerun():
    """Rerunning transformation on the same input order produces the exact same booking_ids."""
    df1 = transform_data(sample_raw_dataframe())
    df2 = transform_data(sample_raw_dataframe())

    assert df1["booking_id"].tolist() == df2["booking_id"].tolist()

def test_all_transformed_booking_ids_are_unique():
    """All transformed booking_ids are unique (is_unique == True)."""
    transformed = transform_data(sample_raw_dataframe())
    assert transformed["booking_id"].is_unique is True

def test_identical_business_rows_receive_unique_sequence_ids():
    """Identical business rows remaining after transformation still receive unique sequence IDs."""
    raw_df = sample_raw_dataframe()

    # Artificially modify row 2 so it is NOT dropped by drop_duplicates but shares identical canonical string fields
    # e.g., create two distinct rows that share canonical source attributes
    row_copy = raw_df.iloc[0].to_dict()
    # Add extra column unselected by REQUIRED_COLUMNS to bypass drop_duplicates
    raw_df_with_extra = raw_df.copy()
    raw_df_with_extra["unselected_col"] = [1, 2, 3]

    transformed = transform_data(raw_df_with_extra)
    assert transformed["booking_id"].is_unique is True
    # Verify sequence suffix format HB-<hash>-01, HB-<hash>-02
    for b_id in transformed["booking_id"]:
        assert b_id.startswith("HB-")
        parts = b_id.split("-")
        assert len(parts) == 3
        assert parts[2].isdigit()

import pytest
import pandas as pd
import numpy as np
from datetime import date
from src.validate import validate_records

def get_base_valid_record():
    """
    Returns a dictionary representing a valid transformed record.
    """
    return {
        "booking_id": "HB-A1B2C3D4E5F678901234",
        "hotel": "Resort Hotel",
        "is_canceled": 0,
        "lead_time": 34,
        "arrival_date": date(2015, 7, 1),
        "stays_in_weekend_nights": 0,
        "stays_in_week_nights": 2,
        "total_nights": 2,
        "adults": 2,
        "children": 0,
        "babies": 0,
        "total_guests": 2,
        "country": "PRT",
        "market_segment": "Direct",
        "distribution_channel": "Direct",
        "is_repeated_guest": 0,
        "previous_cancellations": 0,
        "booking_changes": 0,
        "deposit_type": "No Deposit",
        "customer_type": "Transient",
        "adr": 100.0,
        "booking_value": 200.0,
        "estimated_revenue": 200.0,
        "required_car_parking_spaces": 0,
        "total_of_special_requests": 0,
        "reservation_status": "Check-Out",
        "reservation_status_date": date(2015, 7, 3),
    }

def test_valid_record_accepted():
    df = pd.DataFrame([get_base_valid_record()])
    valid_df, rejected_df = validate_records(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 0

def test_negative_adr_rejected():
    rec = get_base_valid_record()
    rec["adr"] = -50.0
    rec["booking_value"] = -100.0
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "negative adr" in rejected_df.iloc[0]["rejection_reason"]

def test_missing_country_rejected():
    rec = get_base_valid_record()
    rec["country"] = np.nan
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "missing country" in rejected_df.iloc[0]["rejection_reason"]

def test_invalid_arrival_date_rejected():
    rec = get_base_valid_record()
    rec["arrival_date"] = pd.NaT
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "invalid arrival_date" in rejected_df.iloc[0]["rejection_reason"]

def test_zero_adults_rejected():
    rec = get_base_valid_record()
    rec["adults"] = 0
    rec["total_guests"] = 0
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "adults must be >= 1" in rejected_df.iloc[0]["rejection_reason"]

def test_invalid_cancellation_flag_rejected():
    rec = get_base_valid_record()
    rec["is_canceled"] = 5
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "is_canceled must be 0 or 1" in rejected_df.iloc[0]["rejection_reason"]

def test_missing_country_and_negative_adr_both_reasons():
    """Missing country + negative ADR: rejection_reason contains BOTH reasons separated by semicolon."""
    rec = get_base_valid_record()
    rec["country"] = None
    rec["adr"] = -10.0
    df = pd.DataFrame([rec])

    valid_df, rejected_df = validate_records(df)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1

    reason = rejected_df.iloc[0]["rejection_reason"]
    assert "missing country" in reason
    assert "negative adr" in reason
    assert ";" in reason

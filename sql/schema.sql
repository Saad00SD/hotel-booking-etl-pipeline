-- SQL Schema for Hotel Booking ETL Pipeline
-- Table: hotel_bookings
-- Idempotent schema creation with strict integrity and boundary constraints

CREATE TABLE IF NOT EXISTS hotel_bookings (
    booking_id VARCHAR(64) PRIMARY KEY,
    hotel VARCHAR(100) NOT NULL,
    is_canceled SMALLINT NOT NULL CHECK (is_canceled IN (0, 1)),
    lead_time INTEGER NOT NULL CHECK (lead_time >= 0),
    arrival_date DATE NOT NULL,
    stays_in_weekend_nights INTEGER NOT NULL CHECK (stays_in_weekend_nights >= 0),
    stays_in_week_nights INTEGER NOT NULL CHECK (stays_in_week_nights >= 0),
    total_nights INTEGER NOT NULL CHECK (total_nights >= 0),
    adults INTEGER NOT NULL CHECK (adults >= 1),
    children INTEGER NOT NULL CHECK (children >= 0),
    babies INTEGER NOT NULL CHECK (babies >= 0),
    total_guests INTEGER NOT NULL CHECK (total_guests >= 1),
    country VARCHAR(10) NOT NULL,
    market_segment VARCHAR(100),
    distribution_channel VARCHAR(100),
    is_repeated_guest SMALLINT NOT NULL CHECK (is_repeated_guest IN (0, 1)),
    previous_cancellations INTEGER NOT NULL CHECK (previous_cancellations >= 0),
    booking_changes INTEGER NOT NULL CHECK (booking_changes >= 0),
    deposit_type VARCHAR(100),
    customer_type VARCHAR(100),
    adr NUMERIC(12, 2) NOT NULL CHECK (adr >= 0),
    booking_value NUMERIC(14, 2) NOT NULL CHECK (booking_value >= 0),
    estimated_revenue NUMERIC(14, 2) NOT NULL CHECK (estimated_revenue >= 0),
    required_car_parking_spaces INTEGER NOT NULL CHECK (required_car_parking_spaces >= 0),
    total_of_special_requests INTEGER NOT NULL CHECK (total_of_special_requests >= 0),
    reservation_status VARCHAR(100),
    reservation_status_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SQL Index Optimization Definitions for Hotel Booking ETL Pipeline
-- Carefully selected, minimal set of B-Tree indexes aligned with analytical workloads.
-- Note: Indexes improve read performance for selective filtering/grouping, but introduce 
-- storage overhead and slight write degradation during high-volume bulk upserts.

-- 1. Single Column Index: arrival_date
-- Query Supported: Analytical date window queries (BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD').
-- Rationale: B-Tree index allows rapid scanning of contiguous date ranges without scanning the entire table.
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_arrival_date 
ON hotel_bookings (arrival_date);


-- 2. Single Column Index: country
-- Query Supported: Top countries ranking and country-level cancellation analysis.
-- Rationale: Speeds up selective filtering for high-volume origin countries (e.g. WHERE country = 'PRT').
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_country 
ON hotel_bookings (country);


-- 3. Composite Index: (hotel, arrival_date)
-- Query Supported: Hotel-specific temporal revenue aggregations (Monthly revenue per hotel property).
-- Rationale: Compound index orders data first by hotel brand then by arrival date, enabling index-only or bitmap scans for multi-column predicates.
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_hotel_arrival 
ON hotel_bookings (hotel, arrival_date);


-- 4. Composite Index: (country, arrival_date)
-- Query Supported: Performance demonstration selective query (Country + Date Range filter).
-- Rationale: Pinpoints rows matching specific country and date windows efficiently.
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_country_arrival 
ON hotel_bookings (country, arrival_date);

-- Performance Benchmarking & EXPLAIN ANALYZE Demonstration Script
-- Instructions: Run each query with EXPLAIN ANALYZE before and after creating the index.
-- Record planning time, execution time, scan method (Seq Scan vs. Index Scan / Bitmap Heap Scan), 
-- and total cost to evaluate actual database optimizer behavior.

-- ============================================================================
-- DEMONSTRATION 1: Selective Country & Date Range Filter
-- Supported Index: idx_hotel_bookings_country_arrival (country, arrival_date)
-- ============================================================================

-- Step 1: Run EXPLAIN ANALYZE BEFORE Index Creation
-- (Optional: DROP INDEX IF EXISTS idx_hotel_bookings_country_arrival;)
EXPLAIN ANALYZE
SELECT 
    booking_id,
    hotel,
    country,
    arrival_date,
    adr,
    estimated_revenue
FROM 
    hotel_bookings
WHERE 
    country = 'PRT'
    AND arrival_date BETWEEN '2016-01-01' AND '2016-03-31';

-- Step 2: Create Composite Index
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_country_arrival 
ON hotel_bookings (country, arrival_date);

-- Step 3: Run EXPLAIN ANALYZE AFTER Index Creation
EXPLAIN ANALYZE
SELECT 
    booking_id,
    hotel,
    country,
    arrival_date,
    adr,
    estimated_revenue
FROM 
    hotel_bookings
WHERE 
    country = 'PRT'
    AND arrival_date BETWEEN '2016-01-01' AND '2016-03-31';

/*
Plan Evaluation Guide:
- BEFORE INDEX: PostgreSQL will typically execute a Sequential Scan over all ~85k table rows, evaluating the filter condition on each page.
- AFTER INDEX: PostgreSQL may utilize a Bitmap Index Scan or Index Scan on idx_hotel_bookings_country_arrival to retrieve matching tuples directly.
- NOTE: The PostgreSQL query optimizer dynamically chooses execution plans based on table statistics, selectivity, page costs, and buffer caches.
*/


-- ============================================================================
-- DEMONSTRATION 2: Hotel & Arrival Date Window Aggregation
-- Supported Index: idx_hotel_bookings_hotel_arrival (hotel, arrival_date)
-- ============================================================================

-- Step 1: Run EXPLAIN ANALYZE BEFORE Index Creation
-- (Optional: DROP INDEX IF EXISTS idx_hotel_bookings_hotel_arrival;)
EXPLAIN ANALYZE
SELECT 
    hotel,
    arrival_date,
    COUNT(booking_id) AS total_bookings,
    SUM(estimated_revenue) AS daily_revenue
FROM 
    hotel_bookings
WHERE 
    hotel = 'Resort Hotel'
    AND arrival_date BETWEEN '2017-01-01' AND '2017-03-31'
GROUP BY 
    hotel, arrival_date
ORDER BY 
    arrival_date;

-- Step 2: Create Composite Index
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_hotel_arrival 
ON hotel_bookings (hotel, arrival_date);

-- Step 3: Run EXPLAIN ANALYZE AFTER Index Creation
EXPLAIN ANALYZE
SELECT 
    hotel,
    arrival_date,
    COUNT(booking_id) AS total_bookings,
    SUM(estimated_revenue) AS daily_revenue
FROM 
    hotel_bookings
WHERE 
    hotel = 'Resort Hotel'
    AND arrival_date BETWEEN '2017-01-01' AND '2017-03-31'
GROUP BY 
    hotel, arrival_date
ORDER BY 
    arrival_date;

/*
Plan Evaluation Guide:
- BEFORE INDEX: Full table scan with per-row predicate checking and hash aggregation.
- AFTER INDEX: Composite B-Tree index scan targeting rows where hotel = 'Resort Hotel' and date falls in range.
*/


-- ============================================================================
-- DEMONSTRATION 3: Short Date Window Search
-- Supported Index: idx_hotel_bookings_arrival_date (arrival_date)
-- ============================================================================

-- Step 1: Run EXPLAIN ANALYZE BEFORE Index Creation
-- (Optional: DROP INDEX IF EXISTS idx_hotel_bookings_arrival_date;)
EXPLAIN ANALYZE
SELECT 
    arrival_date,
    COUNT(booking_id) AS total_bookings,
    SUM(estimated_revenue) AS total_revenue
FROM 
    hotel_bookings
WHERE 
    arrival_date BETWEEN '2016-06-01' AND '2016-06-15'
GROUP BY 
    arrival_date
ORDER BY 
    arrival_date;

-- Step 2: Create Single Column Index
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_arrival_date 
ON hotel_bookings (arrival_date);

-- Step 3: Run EXPLAIN ANALYZE AFTER Index Creation
EXPLAIN ANALYZE
SELECT 
    arrival_date,
    COUNT(booking_id) AS total_bookings,
    SUM(estimated_revenue) AS total_revenue
FROM 
    hotel_bookings
WHERE 
    arrival_date BETWEEN '2016-06-01' AND '2016-06-15'
GROUP BY 
    arrival_date
ORDER BY 
    arrival_date;

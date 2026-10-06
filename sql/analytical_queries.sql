-- Analytical SQL Queries for Hotel Booking Dataset

-- ============================================================================
-- QUERY 1: Monthly Realized Estimated Revenue by Hotel
-- Purpose: Analyze monthly revenue performance across hotel properties.
-- Note: estimated_revenue naturally evaluates to 0 for canceled bookings.
-- ============================================================================
SELECT 
    TO_CHAR(arrival_date, 'YYYY-MM') AS year_month,
    hotel,
    COUNT(booking_id) AS total_bookings,
    SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END) AS confirmed_bookings,
    ROUND(SUM(booking_value), 2) AS total_booking_value,
    ROUND(SUM(estimated_revenue), 2) AS total_realized_revenue
FROM 
    hotel_bookings
GROUP BY 
    1, 2
ORDER BY 
    year_month ASC, 
    total_realized_revenue DESC;


-- ============================================================================
-- QUERY 2: Cancellation Rate by Country (Minimum 100 Bookings)
-- Purpose: Identify high-risk origin countries by cancellation percentage using NULLIF safety.
-- ============================================================================
SELECT 
    country,
    COUNT(booking_id) AS total_bookings,
    SUM(is_canceled) AS cancelled_bookings,
    ROUND(CAST(SUM(is_canceled) * 100.0 / NULLIF(COUNT(booking_id), 0) AS NUMERIC), 2) AS cancellation_rate_pct
FROM 
    hotel_bookings
GROUP BY 
    country
HAVING 
    COUNT(booking_id) >= 100
ORDER BY 
    cancellation_rate_pct DESC, 
    total_bookings DESC;


-- ============================================================================
-- QUERY 3: Average ADR, Booking Count, Potential Value & Realized Revenue by Market Segment
-- Purpose: Measure yield and volume across market distribution channels.
-- ============================================================================
SELECT 
    COALESCE(market_segment, 'Unknown') AS market_segment,
    COUNT(booking_id) AS booking_count,
    ROUND(AVG(adr), 2) AS average_adr,
    ROUND(SUM(booking_value), 2) AS total_booking_value,
    ROUND(SUM(estimated_revenue), 2) AS total_estimated_revenue
FROM 
    hotel_bookings
GROUP BY 
    market_segment
ORDER BY 
    total_estimated_revenue DESC;


-- ============================================================================
-- QUERY 4: Top 10 Countries by Bookings
-- Purpose: Rank primary geographical markets with volume, total revenue, and average lead time.
-- ============================================================================
SELECT 
    country,
    COUNT(booking_id) AS total_bookings,
    ROUND(SUM(estimated_revenue), 2) AS total_realized_revenue,
    ROUND(AVG(lead_time), 1) AS avg_lead_time_days
FROM 
    hotel_bookings
GROUP BY 
    country
ORDER BY 
    total_bookings DESC
LIMIT 10;


-- ============================================================================
-- QUERY 5: Average Length of Stay by Customer Type
-- Purpose: Understand duration-of-stay dynamics across distinct customer personas.
-- ============================================================================
SELECT 
    COALESCE(customer_type, 'Unknown') AS customer_type,
    COUNT(booking_id) AS booking_count,
    ROUND(AVG(stays_in_weekend_nights), 2) AS avg_weekend_nights,
    ROUND(AVG(stays_in_week_nights), 2) AS avg_week_nights,
    ROUND(AVG(total_nights), 2) AS avg_total_nights
FROM 
    hotel_bookings
GROUP BY 
    customer_type
ORDER BY 
    avg_total_nights DESC;

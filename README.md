# Hotel Booking ETL Pipeline

An end-to-end data engineering project that extracts raw hotel booking data from AWS S3, performs data cleaning, transformation and validation using Python, loads validated records into PostgreSQL, and demonstrates SQL analytics and query optimization.

This project was developed as an Associate Data Engineer technical assessment.

---

## Project Overview

The pipeline processes a hotel booking dataset containing approximately 119,390 raw records.

The main objectives are:

- Extract raw CSV data from AWS S3
- Clean and standardize source data
- Remove duplicate records
- Handle missing values
- Create derived business fields
- Validate business and data quality rules
- Separate valid and rejected records
- Load clean records into PostgreSQL
- Store processed and rejected outputs in AWS S3
- Run analytical SQL queries
- Demonstrate query optimization using PostgreSQL indexes and `EXPLAIN ANALYZE`

---

## Architecture

```mermaid
flowchart TD
    A[Raw Hotel Booking CSV] --> B[AWS S3 - raw/]
    B --> C[Python Extract]
    C --> D[Transform & Clean]
    D --> E[Data Validation]

    E -->|Valid Records| F[Processed CSV]
    E -->|Rejected Records| G[Rejected CSV + Reasons]

    F --> H[AWS S3 - processed/]
    G --> I[AWS S3 - rejected/]

    F --> J[PostgreSQL Staging Table]
    J --> K[Upsert into hotel_bookings]

    K --> L[Analytical SQL Queries]
    K --> M[Indexes + EXPLAIN ANALYZE]
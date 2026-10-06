import sys
import os
import pandas as pd

from src.config import (
    S3_BUCKET_NAME,
    S3_PROCESSED_KEY,
    S3_REJECTED_KEY,
    PROCESSED_DATA_PATH,
    REJECTED_DATA_PATH,
    ALLOW_LOCAL_FALLBACK
)
from src.logger import get_logger
from src.extract import extract_from_s3
from src.transform import transform_data
from src.validate import validate_records
from src.s3_utils import upload_file_to_s3
from src.database import init_db
from src.load import load_to_postgres

logger = get_logger("hotel_etl_runner")

def run_pipeline():
    """
    Main orchestration entry point for Hotel Booking ETL Pipeline.
    Executes extraction, transformation, validation, storage, S3 sync, and PostgreSQL loading.
    Infrastructure failures (S3, PostgreSQL) will terminate execution with a non-zero exit code.
    """
    logger.info("====================================")
    logger.info("HOTEL BOOKING ETL PIPELINE STARTED")
    logger.info("====================================")

    try:
        # Step 1: Extraction
        raw_df = extract_from_s3()
        source_count = len(raw_df)

        # Step 2: Transformation
        transformed_df = transform_data(raw_df)

        # Calculate exact duplicates removed dynamically
        duplicates_removed = source_count - len(transformed_df)

        # Step 3: Validation
        valid_df, rejected_df = validate_records(transformed_df)
        valid_count = len(valid_df)
        rejected_count = len(rejected_df)
        rejection_pct = (rejected_count / len(transformed_df) * 100.0) if len(transformed_df) > 0 else 0.0

        # Step 4: Save Rejected Records locally
        os.makedirs(os.path.dirname(REJECTED_DATA_PATH), exist_ok=True)
        rejected_df.to_csv(REJECTED_DATA_PATH, index=False)
        logger.info(f"Saved {rejected_count} rejected records locally to {REJECTED_DATA_PATH}")

        # Step 5: Save Cleaned Records locally
        os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
        valid_df.to_csv(PROCESSED_DATA_PATH, index=False)
        logger.info(f"Saved {valid_count} cleaned valid records locally to {PROCESSED_DATA_PATH}")

        # Step 6: Upload files to S3 (Mandatory if S3 Bucket is configured)
        cleaned_upload_status = "skipped"
        rejected_upload_status = "skipped"

        if S3_BUCKET_NAME and S3_BUCKET_NAME != "your_bucket_name":
            logger.info(f"Uploading processed outputs to AWS S3 bucket '{S3_BUCKET_NAME}'...")
            upload_file_to_s3(str(PROCESSED_DATA_PATH), S3_BUCKET_NAME, S3_PROCESSED_KEY)
            cleaned_upload_status = "successful"

            upload_file_to_s3(str(REJECTED_DATA_PATH), S3_BUCKET_NAME, S3_REJECTED_KEY)
            rejected_upload_status = "successful"
        else:
            logger.info("S3_BUCKET_NAME not configured in environment. Skipping AWS S3 upload step.")

        # Step 7 & 8: PostgreSQL Database Initialization & Loading (Mandatory Infrastructure Step)
        logger.info("Initializing PostgreSQL schema and executing batch upsert...")
        init_db()
        load_to_postgres(valid_df)
        db_load_status = "successful"

        # Step 9: Print Final Pipeline Summary Box
        summary_msg = f"""
====================================
HOTEL BOOKING ETL PIPELINE SUMMARY
====================================

Source records:             {source_count}
Duplicates removed:         {duplicates_removed}
Valid records:              {valid_count}
Rejected records:           {rejected_count}
Rejection percentage:       {rejection_pct:.2f}%
Processed S3 upload:        {cleaned_upload_status}
Rejected S3 upload:         {rejected_upload_status}
PostgreSQL load:            {db_load_status}

Pipeline completed successfully.
====================================
"""
        print(summary_msg)
        logger.info("HOTEL BOOKING ETL PIPELINE COMPLETED SUCCESSFULLY.")

    except Exception as e:
        logger.error("====================================")
        logger.error(f"PIPELINE FAILED: Infrastructure error encountered: {e}")
        logger.error("====================================")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()

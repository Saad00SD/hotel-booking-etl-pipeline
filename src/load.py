import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from src.database import get_db_engine
from src.logger import get_logger

logger = get_logger(__name__)

DB_COLUMNS = [
    "booking_id", "hotel", "is_canceled", "lead_time", "arrival_date",
    "stays_in_weekend_nights", "stays_in_week_nights", "total_nights",
    "adults", "children", "babies", "total_guests", "country",
    "market_segment", "distribution_channel", "is_repeated_guest",
    "previous_cancellations", "booking_changes", "deposit_type",
    "customer_type", "adr", "booking_value", "estimated_revenue",
    "required_car_parking_spaces", "total_of_special_requests",
    "reservation_status", "reservation_status_date"
]

def load_to_postgres(
    valid_df: pd.DataFrame,
    engine: Engine = None,
    table_name: str = "hotel_bookings",
    chunksize: int = 5000
) -> bool:
    """
    Loads valid hotel booking records into PostgreSQL database in batches.
    Employs temporary staging table upsert (ON CONFLICT DO UPDATE) within an explicit transaction.
    Raises an exception if any database infrastructure error occurs to fail the pipeline cleanly.

    :param valid_df: Validated pandas DataFrame.
    :param engine: SQLAlchemy Engine instance.
    :param table_name: Target PostgreSQL table name.
    :param chunksize: Batch size for database insert operations.
    :return: True if load succeeded. Raises exception on infrastructure failure.
    """
    logger.info("====================================")
    logger.info("STAGE 4: DATABASE LOADING STARTED")
    logger.info("====================================")

    if valid_df is None or valid_df.empty:
        logger.warning("No valid records to load into database.")
        return True

    if engine is None:
        engine = get_db_engine()

    # Align DataFrame columns with database schema
    df_to_load = valid_df[[col for col in DB_COLUMNS if col in valid_df.columns]].copy()
    row_count = len(df_to_load)

    # Explicit validation check before staging/upsert
    if df_to_load["booking_id"].duplicated().any():
        dup_sample = list(df_to_load[df_to_load["booking_id"].duplicated(keep=False)]["booking_id"].unique()[:5])
        err_msg = f"Duplicate booking_id values detected prior to database staging/upsert! Sample IDs: {dup_sample}"
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.info(f"Preparing batch load of {row_count} records into target table '{table_name}' with chunksize={chunksize}...")

    try:
        with engine.begin() as conn:
            # 1. Create a temporary staging table matching schema
            conn.execute(text(f"CREATE TEMP TABLE staging_{table_name} (LIKE {table_name} INCLUDING DEFAULTS) ON COMMIT DROP;"))

            # 2. Insert into staging table using pandas to_sql in chunks
            df_to_load.to_sql(
                name=f"staging_{table_name}",
                con=conn,
                if_exists="append",
                index=False,
                chunksize=chunksize,
                method="multi"
            )

            # 3. Upsert from staging table into target table idempotently
            cols_str = ", ".join(df_to_load.columns)
            update_assignments = ", ".join([f"{col} = EXCLUDED.{col}" for col in df_to_load.columns if col != "booking_id"])

            upsert_sql = text(f"""
                INSERT INTO {table_name} ({cols_str})
                SELECT {cols_str} FROM staging_{table_name}
                ON CONFLICT (booking_id) 
                DO UPDATE SET {update_assignments};
            """)

            conn.execute(upsert_sql)
            logger.info("Idempotent database upsert completed successfully.")

        logger.info(f"Database load completed successfully. {row_count} records loaded/upserted.")
        return True

    except Exception as e:
        logger.error(f"PostgreSQL Database Load Operation Failed: {e}", exc_info=True)
        raise RuntimeError(f"PostgreSQL database loading failed: {e}") from e

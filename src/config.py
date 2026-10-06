import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# AWS S3 Configurations
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your_access_key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your_secret_key")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your_bucket_name")
S3_RAW_KEY = os.getenv("S3_RAW_KEY", "raw/hotel_bookings.csv")
S3_PROCESSED_KEY = os.getenv("S3_PROCESSED_KEY", "processed/hotel_bookings_cleaned.csv")
S3_REJECTED_KEY = os.getenv("S3_REJECTED_KEY", "rejected/hotel_bookings_rejected.csv")

# ETL Execution Controls
ALLOW_LOCAL_FALLBACK = os.getenv("ALLOW_LOCAL_FALLBACK", "false").lower() in ("true", "1", "yes")

# PostgreSQL Database Configurations
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "hotel_etl")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

# Local Storage Directory Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "hotel_bookings.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "hotel_bookings_cleaned.csv"
REJECTED_DATA_PATH = DATA_DIR / "rejected" / "hotel_bookings_rejected.csv"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "pipeline.log"

def get_db_url() -> str:
    """
    Constructs and returns the PostgreSQL database connection URL for SQLAlchemy.
    """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

import os
import pandas as pd
from src.config import S3_BUCKET_NAME, S3_RAW_KEY, RAW_DATA_PATH, ALLOW_LOCAL_FALLBACK
from src.s3_utils import read_csv_from_s3
from src.logger import get_logger

logger = get_logger(__name__)

def extract_from_s3(
    bucket_name: str = S3_BUCKET_NAME,
    raw_key: str = S3_RAW_KEY,
    local_fallback_path: str = str(RAW_DATA_PATH),
    allow_fallback: bool = ALLOW_LOCAL_FALLBACK
) -> pd.DataFrame:
    """
    Extracts raw hotel booking CSV dataset from AWS S3 into a pandas DataFrame.
    If ALLOW_LOCAL_FALLBACK is False, an S3 extraction failure will terminate the pipeline.
    If ALLOW_LOCAL_FALLBACK is True, it will attempt loading from local fallback CSV path.

    :param bucket_name: S3 bucket name.
    :param raw_key: S3 object key path for raw dataset.
    :param local_fallback_path: Local CSV path for fallback extraction.
    :param allow_fallback: Boolean flag controlling local fallback permission.
    :return: pd.DataFrame containing raw hotel bookings data.
    """
    logger.info("====================================")
    logger.info("STAGE 1: EXTRACTION STARTED")
    logger.info("====================================")

    df = None
    source_identifier = f"s3://{bucket_name}/{raw_key}"

    try:
        logger.info(f"Attempting extraction from S3 source: {source_identifier}")
        df = read_csv_from_s3(bucket_name, raw_key)
        logger.info(f"Extraction successful from AWS S3: {source_identifier}")
    except Exception as s3_err:
        logger.error(f"S3 extraction failed for {source_identifier}: {s3_err}")
        if allow_fallback:
            logger.warning(f"ALLOW_LOCAL_FALLBACK=True. Attempting local fallback: {local_fallback_path}")
            if os.path.exists(local_fallback_path):
                try:
                    df = pd.read_csv(local_fallback_path)
                    source_identifier = f"Local File: {local_fallback_path}"
                    logger.info(f"Extraction successful from local fallback source: {local_fallback_path}")
                except Exception as local_err:
                    logger.error(f"Local fallback extraction also failed: {local_err}")
                    raise RuntimeError(f"Extraction failed for both S3 ({source_identifier}) and local path ({local_fallback_path}).") from local_err
            else:
                logger.error(f"Local fallback file not found at {local_fallback_path}")
                raise RuntimeError(f"S3 extraction failed and local fallback file is missing.") from s3_err
        else:
            logger.error("ALLOW_LOCAL_FALLBACK=False. Mandatory S3 extraction failed. Terminating pipeline.")
            raise RuntimeError(f"Mandatory AWS S3 extraction failed for {source_identifier}: {s3_err}") from s3_err

    if df is not None:
        num_rows, num_cols = df.shape
        logger.info(f"Extraction Summary | Source: {source_identifier} | Rows: {num_rows} | Columns: {num_cols}")
        return df
    else:
        raise ValueError("Extracted DataFrame is empty or None.")

import io
import os
import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from src.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
from src.logger import get_logger

logger = get_logger(__name__)

def get_s3_client():
    """
    Initializes and returns a boto3 S3 client using configured environment credentials.
    """
    try:
        kwargs = {"region_name": AWS_REGION}
        if AWS_ACCESS_KEY_ID and AWS_ACCESS_KEY_ID != "your_access_key":
            kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        if AWS_SECRET_ACCESS_KEY and AWS_SECRET_ACCESS_KEY != "your_secret_key":
            kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

        s3_client = boto3.client("s3", **kwargs)
        return s3_client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        raise

def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Reads a CSV file directly from an S3 bucket into a Pandas DataFrame.

    :param bucket: Name of S3 bucket.
    :param key: S3 object key path.
    :return: pd.DataFrame
    """
    try:
        s3_client = get_s3_client()
        logger.info(f"Attempting to fetch s3://{bucket}/{key}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read()
        df = pd.read_csv(io.BytesIO(content))
        logger.info(f"Successfully read CSV from s3://{bucket}/{key} with shape {df.shape}")
        return df
    except (BotoCoreError, ClientError, NoCredentialsError) as e:
        logger.error(f"S3 Error reading s3://{bucket}/{key}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading s3://{bucket}/{key}: {e}")
        raise

def upload_file_to_s3(local_path: str, bucket: str, key: str) -> bool:
    """
    Uploads a local file to an S3 bucket. Raises exception on failure.

    :param local_path: Path to local file.
    :param bucket: Name of S3 bucket.
    :param key: Destination S3 key path.
    :return: True if successful. Raises RuntimeError on failure.
    """
    if not os.path.exists(local_path):
        err_msg = f"Cannot upload: local file {local_path} does not exist."
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    try:
        s3_client = get_s3_client()
        logger.info(f"Uploading {local_path} -> s3://{bucket}/{key}")
        s3_client.upload_file(local_path, bucket, key)
        logger.info(f"Successfully uploaded {local_path} to s3://{bucket}/{key}")
        return True
    except (BotoCoreError, ClientError, NoCredentialsError) as e:
        err_msg = f"Failed to upload {local_path} to s3://{bucket}/{key}: {e}"
        logger.error(err_msg)
        raise RuntimeError(err_msg) from e
    except Exception as e:
        err_msg = f"Unexpected error uploading {local_path} to s3://{bucket}/{key}: {e}"
        logger.error(err_msg)
        raise RuntimeError(err_msg) from e

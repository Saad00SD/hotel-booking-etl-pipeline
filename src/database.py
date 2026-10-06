import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.config import get_db_url, BASE_DIR
from src.logger import get_logger

logger = get_logger(__name__)

_engine = None

def get_db_engine() -> Engine:
    """
    Creates or returns cached SQLAlchemy Engine instance with connection pooling.
    """
    global _engine
    if _engine is None:
        db_url = get_db_url()
        try:
            _engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            logger.info("Successfully created SQLAlchemy database engine.")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    return _engine

def execute_sql_file(file_path: str, engine: Engine = None) -> bool:
    """
    Executes a SQL script file using the provided SQLAlchemy engine.

    :param file_path: Absolute or relative path to SQL script file.
    :param engine: SQLAlchemy Engine instance.
    :return: True if successful, False otherwise.
    """
    if engine is None:
        engine = get_db_engine()

    sql_path = Path(file_path)
    if not sql_path.is_absolute():
        sql_path = BASE_DIR / file_path

    if not sql_path.exists():
        logger.error(f"SQL file not found at {sql_path}")
        return False

    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split multi-statement SQL files safely
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))

        logger.info(f"Successfully executed SQL script: {sql_path.name}")
        return True
    except Exception as e:
        logger.error(f"Error executing SQL file {sql_path}: {e}")
        raise

def init_db(engine: Engine = None) -> bool:
    """
    Initializes PostgreSQL database schema by running sql/schema.sql idempotently.
    """
    logger.info("Initializing database schema...")
    schema_path = BASE_DIR / "sql" / "schema.sql"
    return execute_sql_file(schema_path, engine)

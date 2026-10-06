import os
import logging
from pathlib import Path

def get_logger(name: str = "hotel_etl", log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and returns a configured logger instance supporting file and console output.

    :param name: Name of the logger.
    :param log_file: Optional path to log file. Defaults to logs/pipeline.log.
    :param level: Logging level.
    :return: Formatted logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Format for log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file is None:
        base_dir = Path(__file__).resolve().parent.parent
        log_dir = base_dir / "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = str(log_dir / "pipeline.log")
    else:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

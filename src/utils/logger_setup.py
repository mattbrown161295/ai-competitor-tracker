"""
Logging configuration using loguru.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger


def setup_logging(config: Dict[str, Any] = None):
    """Configure logging based on configuration."""
    if config is None:
        config = {}

    logging_config = config.get("logging", {})

    # Remove default handler
    logger.remove()

    # Console handler
    log_level = logging_config.get("level", "INFO")
    log_format = logging_config.get(
        "format", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File handler
    log_dir = Path(logging_config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "competitor_tracker.log"

    logger.add(
        str(log_file),
        format=log_format,
        level=log_level,
        rotation=logging_config.get("rotation", "100 MB"),
        retention=logging_config.get("retention", "30 days"),
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    logger.info(f"Logging configured. Level: {log_level}, Log file: {log_file}")


def get_logger():
    """Get the configured logger instance."""
    return logger

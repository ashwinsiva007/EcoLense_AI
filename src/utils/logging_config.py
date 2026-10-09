"""Reusable logging configuration for EconLens AI.

Provides structured console and file logging with idempotency, custom formatting,
and directory management.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import get_settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_CONFIGURED = False


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: Optional[bool] = None,
    log_dir: Optional[Path] = None,
) -> logging.Logger:
    """Configures root logger with console and optional file handlers.

    Idempotent: Subsequent calls update level but will not add duplicate handlers.

    Args:
        log_level: Severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_to_file: Whether to write logs to a file in log_dir.
        log_dir: Directory to store log files.

    Returns:
        logging.Logger: The configured root logger.
    """
    global _CONFIGURED

    settings = get_settings()
    level_str = (log_level or settings.log_level).upper()
    numeric_level = getattr(logging, level_str, logging.INFO)
    should_log_to_file = (
        log_to_file if log_to_file is not None else settings.log_to_file
    )
    target_log_dir = log_dir or settings.log_dir

    root_logger = logging.getLogger("econlens_ai")
    root_logger.setLevel(numeric_level)

    if _CONFIGURED:
        root_logger.setLevel(numeric_level)
        return root_logger

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler
    if should_log_to_file:
        try:
            target_log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = target_log_dir / "econlens_ai.log"
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as err:
            console_handler.setLevel(logging.WARNING)
            root_logger.warning("Failed to initialize file logger: %s", err)

    root_logger.propagate = False
    _CONFIGURED = True
    root_logger.debug(
        "Logging initialized at level %s (file_logging=%s)",
        level_str,
        should_log_to_file,
    )
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Retrieves a namespaced child logger under 'econlens_ai'.

    Args:
        name: Name of the submodule or component.

    Returns:
        logging.Logger: Namespaced logger instance.
    """
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(f"econlens_ai.{name}")

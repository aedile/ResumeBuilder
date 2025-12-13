"""Structured JSON logging with PII filtering.

CONSTITUTION Priority 0: Security - PII filtering is critical
CONSTITUTION Priority 3: TDD GREEN Phase
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class PIIFilter(logging.Filter):
    """Filter to redact PII from log messages.

    Redacts:
    - Email addresses
    - Phone numbers (various formats)
    """

    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record by redacting PII from message.

        Args:
            record: Log record to filter.

        Returns:
            True (always allow record through, but modify message).
        """
        if isinstance(record.msg, str):
            # Redact emails
            record.msg = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", record.msg)
            # Redact phone numbers
            record.msg = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", record.msg)

        return True


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: Log record to format.

        Returns:
            JSON formatted log string.
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation_id if present in extra
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    log_dir: Path | None = None,
    log_file: str | None = None,
) -> logging.Logger:
    """Set up structured JSON logging with PII filtering.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_dir: Directory for log files (created if doesn't exist).
        log_file: Specific log file path (overrides log_dir).

    Returns:
        Configured root logger.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter and filter
    json_formatter = JSONFormatter()
    pii_filter = PIIFilter()

    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(pii_filter)
    root_logger.addHandler(console_handler)

    # File handler (if log path specified)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(pii_filter)
        root_logger.addHandler(file_handler)
    elif log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / "resume_builder.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(pii_filter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)

"""Tests for logging configuration with PHI filtering.

CONSTITUTION Priority 0: Security - PII filtering is critical
CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

import json
import logging
from pathlib import Path

from resume_builder.utils.logging import (
    PIIFilter,
    get_logger,
    setup_logging,
)


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_creates_logger(self, tmp_path: Path) -> None:
        """Logger is created with correct level."""
        logger = setup_logging(level="INFO", log_dir=tmp_path)
        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self, tmp_path: Path) -> None:
        """Logger can be configured with DEBUG level."""
        logger = setup_logging(level="DEBUG", log_dir=tmp_path)
        assert logger.level == logging.DEBUG

    def test_setup_logging_creates_log_directory(self, tmp_path: Path) -> None:
        """Log directory is created if it doesn't exist."""
        log_dir = tmp_path / "logs"
        assert not log_dir.exists()
        setup_logging(log_dir=log_dir)
        assert log_dir.exists()


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self) -> None:
        """get_logger returns a logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_different_names(self) -> None:
        """Different names return different logger instances."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1.name != logger2.name


class TestJSONFormatting:
    """Tests for JSON log formatting."""

    def test_json_format_output(self, tmp_path: Path) -> None:
        """Log output is valid JSON."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_dir=tmp_path / "logs", log_file=str(log_file))
        logger.info("Test message")

        # Read log file and verify JSON
        log_content = log_file.read_text()
        log_entry = json.loads(log_content.strip())

        assert log_entry["message"] == "Test message"
        assert log_entry["level"] == "INFO"
        assert "timestamp" in log_entry

    def test_json_includes_all_fields(self, tmp_path: Path) -> None:
        """JSON log includes all required fields."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_dir=tmp_path / "logs", log_file=str(log_file))
        logger.warning("Warning message")

        log_content = log_file.read_text()
        log_entry = json.loads(log_content.strip())

        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "message" in log_entry
        assert "logger" in log_entry


class TestPIIFilter:
    """Tests for PII filtering."""

    def test_pii_filter_redacts_email(self) -> None:
        """Emails are replaced with [REDACTED]."""
        pii_filter = PIIFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User email is john.doe@example.com in the system",
            args=(),
            exc_info=None,
        )

        result = pii_filter.filter(record)
        assert result is True
        assert "john.doe@example.com" not in record.msg
        assert "[REDACTED_EMAIL]" in record.msg

    def test_pii_filter_redacts_phone(self) -> None:
        """Phone numbers are replaced with [REDACTED]."""
        pii_filter = PIIFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Call me at 555-123-4567 or (555) 987-6543",
            args=(),
            exc_info=None,
        )

        result = pii_filter.filter(record)
        assert result is True
        assert "555-123-4567" not in record.msg
        assert "(555) 987-6543" not in record.msg
        assert "[REDACTED_PHONE]" in record.msg

    def test_pii_filter_preserves_non_pii(self) -> None:
        """Non-PII messages are unchanged."""
        pii_filter = PIIFilter()
        original_msg = "Processing request for user ID 12345"
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        result = pii_filter.filter(record)
        assert result is True
        assert record.msg == original_msg


class TestCorrelationID:
    """Tests for correlation ID support."""

    def test_correlation_id_included(self, tmp_path: Path) -> None:
        """Correlation ID appears in log output."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_dir=tmp_path / "logs", log_file=str(log_file))

        # Log with correlation ID in extra
        logger.info("Test message", extra={"correlation_id": "abc-123-xyz"})

        log_content = log_file.read_text()
        log_entry = json.loads(log_content.strip())

        assert log_entry["correlation_id"] == "abc-123-xyz"

    def test_correlation_id_optional(self, tmp_path: Path) -> None:
        """Correlation ID is optional - logs work without it."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_dir=tmp_path / "logs", log_file=str(log_file))

        logger.info("Test message without correlation ID")

        log_content = log_file.read_text()
        log_entry = json.loads(log_content.strip())

        # Should not error, correlation_id just won't be present
        assert log_entry["message"] == "Test message without correlation ID"

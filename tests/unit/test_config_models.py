"""Tests for configuration models.

TDD RED phase: These tests define requirements for config models.
"""

import pytest
from pydantic import ValidationError

from resume_builder.models.config import (
    AppConfig,
    ContactInfo,
    UserPreferences,
)


class TestContactInfo:
    """Tests for ContactInfo model."""

    def test_contact_info_with_email(self) -> None:
        """ContactInfo validates email format."""
        contact = ContactInfo(
            email="test@example.com",
            phone="555-1234",
        )
        assert contact.email == "test@example.com"
        assert contact.phone == "555-1234"

    def test_contact_info_invalid_email_no_at(self) -> None:
        """ContactInfo rejects address with no @ sign."""
        with pytest.raises(ValidationError):
            ContactInfo(email="not-an-email")

    def test_contact_info_invalid_email_no_tld(self) -> None:
        """ContactInfo rejects address with no TLD (e.g. user@localhost)."""
        with pytest.raises(ValidationError):
            ContactInfo(email="user@localhost")

    def test_contact_info_invalid_email_missing_local(self) -> None:
        """ContactInfo rejects address with empty local part (@domain.com)."""
        with pytest.raises(ValidationError):
            ContactInfo(email="@example.com")

    def test_contact_info_invalid_email_spaces(self) -> None:
        """ContactInfo rejects address containing spaces."""
        with pytest.raises(ValidationError):
            ContactInfo(email="user name@example.com")

    def test_contact_info_email_is_normalized(self) -> None:
        """ContactInfo normalizes email to lowercase."""
        contact = ContactInfo(email="User@Example.COM")
        assert contact.email == "user@example.com"


class TestUserPreferences:
    """Tests for UserPreferences model."""

    def test_user_preferences_defaults(self) -> None:
        """UserPreferences has sensible defaults."""
        prefs = UserPreferences()
        assert prefs.default_style == "modern"
        assert prefs.default_length == "one_page"


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_app_config_creation(self) -> None:
        """AppConfig aggregates all config."""
        config = AppConfig(
            contact=ContactInfo(email="test@example.com"),
            preferences=UserPreferences(),
        )
        assert config.contact.email == "test@example.com"
        assert len(config.job_targets) == 0

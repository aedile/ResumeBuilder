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

    def test_contact_info_email_domain_is_normalized(self) -> None:
        """ContactInfo normalizes the email domain to lowercase (RFC 5321)."""
        contact = ContactInfo(email="User@Example.COM")
        # Domain portion must be lowercased; local part is case-preserved per RFC 5321.
        assert contact.email.endswith("@example.com")


class TestUserPreferences:
    """Tests for UserPreferences model."""

    def test_user_preferences_defaults(self) -> None:
        """UserPreferences has sensible defaults."""
        prefs = UserPreferences()
        assert prefs.default_style == "modern"
        assert prefs.default_length == "one_page"


class TestContactInfoLinkedIn:
    """Tests for ContactInfo.linkedin_url field (P2-T11)."""

    def test_contact_info_accepts_linkedin_url(self) -> None:
        """ContactInfo accepts an optional LinkedIn profile URL."""
        contact = ContactInfo(
            email="test@example.com",
            linkedin_url="https://linkedin.com/in/testuser",
        )
        assert contact.linkedin_url == "https://linkedin.com/in/testuser"

    def test_contact_info_linkedin_url_defaults_to_none(self) -> None:
        """ContactInfo.linkedin_url is None when not provided."""
        contact = ContactInfo(email="test@example.com")
        assert contact.linkedin_url is None

    def test_contact_info_all_fields(self) -> None:
        """ContactInfo accepts email, phone, and linkedin_url together."""
        contact = ContactInfo(
            email="alex@example.com",
            phone="555-9876",
            linkedin_url="https://linkedin.com/in/alex",
        )
        assert contact.email == "alex@example.com"
        assert contact.phone == "555-9876"
        assert contact.linkedin_url == "https://linkedin.com/in/alex"


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

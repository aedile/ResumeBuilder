"""Configuration models using Pydantic v2."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactInfo(BaseModel):
    """User contact information.

    Args:
        email: Validated email address.
        phone: Optional phone number (any format accepted).
        linkedin_url: Optional LinkedIn profile URL. Must be http or https
            to prevent injection of javascript: or data: URIs into rendered
            HTML href attributes.
    """

    email: EmailStr
    phone: str | None = None
    linkedin_url: str | None = None

    @field_validator("linkedin_url")
    @classmethod
    def validate_linkedin_url(cls, v: str | None) -> str | None:
        """Reject non-http(s) schemes to prevent URI injection in HTML."""
        if v is None:
            return v
        if not v.startswith(("https://", "http://")):
            raise ValueError(f"linkedin_url must start with https:// or http://; received: {v!r}")
        return v


class UserPreferences(BaseModel):
    """User preferences for resume generation."""

    default_style: str = "modern"
    default_length: str = "one_page"


class JobTarget(BaseModel):
    """Saved job target."""

    id: str
    title: str
    company: str


class AppConfig(BaseModel):
    """Application configuration aggregate."""

    contact: ContactInfo
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    job_targets: list[JobTarget] = []

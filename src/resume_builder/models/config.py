"""Configuration models using Pydantic v2."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """User contact information.

    Args:
        email: Validated email address.
        phone: Optional phone number (any format accepted).
        linkedin_url: Optional LinkedIn profile URL.
    """

    email: EmailStr
    phone: str | None = None
    linkedin_url: str | None = None


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

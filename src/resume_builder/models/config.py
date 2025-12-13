"""Configuration models using Pydantic v2."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ContactInfo(BaseModel):
    """User contact information."""

    email: str
    phone: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
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

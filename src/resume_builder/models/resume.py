"""Resume data models using Pydantic v2.

All models use Pydantic for validation, type safety, and JSON serialization.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, computed_field


class Profile(BaseModel):
    """Personal profile information."""

    first_name: str
    last_name: str
    headline: str
    summary: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        """Computed full name from first and last name."""
        return f"{self.first_name} {self.last_name}"


class Position(BaseModel):
    """Work experience position."""

    company: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    location: Optional[str] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_current(self) -> bool:
        """Check if this is a current position."""
        return self.end_date is None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration(self) -> str:
        """Calculate human-readable duration."""
        if self.end_date:
            years = self.end_date.year - self.start_date.year
            months = self.end_date.month - self.start_date.month
            if months < 0:
                years -= 1
                months += 12
            if years > 0 and months > 0:
                return f"{years} years {months} months"
            elif years > 0:
                return f"{years} years"
            elif months > 0:
                return f"{months} months"
            return "Less than 1 month"
        else:
            return self.start_date.strftime("%b %Y") + " - Present"


class Education(BaseModel):
    """Educational background."""

    school_name: str
    degree_name: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    activities: Optional[str] = None


class Skill(BaseModel):
    """Technical or soft skill."""

    name: str
    category: Optional[str] = None


class Certification(BaseModel):
    """Professional certification."""

    name: str
    authority: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    url: Optional[str] = None


class Project(BaseModel):
    """Portfolio project."""

    title: str
    description: str
    url: Optional[str] = None


class Publication(BaseModel):
    """Published work."""

    title: str
    publisher: str
    publication_date: Optional[date] = None
    url: Optional[str] = None


class Language(BaseModel):
    """Language proficiency."""

    name: str
    proficiency: Optional[str] = None


class Volunteer(BaseModel):
    """Volunteer experience."""

    organization: str
    role: str
    cause: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Honor(BaseModel):
    """Award or honor."""

    title: str
    issuer: str
    date: Optional[date] = None
    description: Optional[str] = None


class Resume(BaseModel):
    """Complete resume aggregate model."""

    profile: Profile
    positions: list[Position] = []
    education: list[Education] = []
    skills: list[Skill] = []
    certifications: list[Certification] = []
    projects: list[Project] = []
    publications: list[Publication] = []
    languages: list[Language] = []
    volunteer: list[Volunteer] = []
    honors: list[Honor] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sorted_positions(self) -> list[Position]:
        """Get positions sorted by start date (most recent first)."""
        return sorted(self.positions, key=lambda p: p.start_date, reverse=True)

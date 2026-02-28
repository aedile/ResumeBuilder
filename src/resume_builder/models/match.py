"""Pydantic models for job matching — JobDescription and MatchReport.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class JobDescription(BaseModel):
    """A target job description for resume matching.

    Args:
        title: Job title (e.g. ``"Senior Software Engineer"``).
        description: Full text of the job posting.
        company: Hiring company name (optional).
        required_skills: Explicit skill list extracted from the posting.
        years_experience: Minimum years of experience required, if stated.
    """

    title: str
    description: str
    company: str | None = None
    required_skills: list[str] = []
    years_experience: int | None = None


class MatchReport(BaseModel):
    """Result of a MatcherAgent analysis session.

    Args:
        overall_score: Composite match score from 0 (no match) to 100 (perfect).
        section_scores: Per-section scores keyed by section name.
        gaps: Skills or qualifications present in the job but absent from resume.
        recommendations: Suggested improvements to increase the match score.
        ranked_positions: Position titles ordered by relevance to the job.
    """

    model_config = ConfigDict(extra="forbid")

    overall_score: int = 0
    section_scores: dict[str, int] = {}
    gaps: list[str] = []
    recommendations: list[str] = []
    ranked_positions: list[str] = []

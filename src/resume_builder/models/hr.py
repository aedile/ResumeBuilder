"""HRReport model — structured output from HRAgent.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HRReport(BaseModel):
    """Structured output returned by HRAgent after reviewing resume text.

    All boolean fields default to the "no-issue" state so that a minimal
    API response only needs to include fields where issues were found.

    Attributes:
        professionalism_score: Overall professional tone score (0-100).
            Scores below 70 indicate issues requiring attention.
        has_grammar_issues: True if grammar or style problems were detected.
        is_formatting_consistent: True if date/formatting is consistent.
        has_placeholders: True if leftover template placeholder text was found.
        issues: Actionable issue descriptions surfaced during review.
        suggestions: Recommended improvements for the candidate.
    """

    model_config = ConfigDict(extra="forbid")

    professionalism_score: int = Field(default=0, ge=0, le=100)
    has_grammar_issues: bool = False
    is_formatting_consistent: bool = True
    has_placeholders: bool = False
    issues: list[str] = []
    suggestions: list[str] = []

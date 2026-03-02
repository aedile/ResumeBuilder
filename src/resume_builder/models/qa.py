"""Pydantic model for QA review results.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class QAReport(BaseModel):
    """Result of a QAAgent review session.

    Args:
        layout_score: Visual hierarchy score from 0 (no structure) to 100 (complete).
        is_accessible: True when no WCAG 2.1 AA violations were found.
        print_ready: True when no print-unfriendly CSS patterns were detected.
        sections_found: Resume section names identified during layout evaluation.
        issues: Accessibility and print-quality violations as actionable strings.
        suggestions: Layout improvement suggestions as actionable strings.
    """

    model_config = ConfigDict(extra="forbid")

    layout_score: int = 0
    is_accessible: bool = False
    print_ready: bool = False
    sections_found: list[str] = []
    issues: list[str] = []
    suggestions: list[str] = []

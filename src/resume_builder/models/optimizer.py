"""Pydantic model for resume optimization results — OptimizedResume.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OptimizedResume(BaseModel):
    """Result of an OptimizerAgent session.

    Args:
        summary: AI-tailored professional summary for the target job.
        optimized_bullets: Mapping of position title to a list of improved
            bullet point strings.
        changes: Human-readable list of changes made during optimization.
    """

    model_config = ConfigDict(extra="forbid")

    summary: str | None = None
    optimized_bullets: dict[str, list[str]] = {}
    changes: list[str] = []

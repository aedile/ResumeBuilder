"""Pydantic model for the final result produced by OrchestratorAgent.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from pydantic import BaseModel

from resume_builder.models.agent import TokenUsage
from resume_builder.models.match import MatchReport
from resume_builder.models.optimizer import OptimizedResume


class FinalResult(BaseModel):
    """The complete output of the orchestration pipeline.

    Produced by ``OrchestratorAgent.run()`` after all agents have executed.
    When the optimizer step fails gracefully, ``optimized`` holds an empty
    ``OptimizedResume`` and ``errors`` records the failure description.

    Args:
        optimized: Optimized resume content. May be empty if the optimizer step
            failed (check ``errors``).
        match: Job-fit analysis from the Matcher Agent. ``None`` only if the
            matching step itself failed (in which case a ``ParseError`` is
            raised rather than returning a FinalResult).
        token_usage: Aggregated API token consumption across all agents.
        errors: Non-fatal error descriptions (e.g. optimizer skipped due to
            failure or approval rejection). Empty list on a fully successful run.
    """

    optimized: OptimizedResume
    match: MatchReport | None = None
    token_usage: TokenUsage = TokenUsage()
    errors: list[str] = []

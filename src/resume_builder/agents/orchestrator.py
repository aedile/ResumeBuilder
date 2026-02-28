"""Orchestrator Agent — coordinates Parser, Matcher, and Optimizer agents.

The OrchestratorAgent runs the full resume optimisation pipeline:
  1. ParserAgent: LinkedIn data → Resume
  2. MatcherAgent: Resume + JobDescription → MatchReport
  3. OptimizerAgent: Resume + JobDescription + MatchReport → OptimizedResume

It manages shared state, handles partial failures gracefully, supports
progress callbacks, and optionally waits for human-in-the-loop approval
between the matching and optimisation steps.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from resume_builder.agents.matcher_agent import MatcherAgent
from resume_builder.agents.optimizer_agent import OptimizerAgent
from resume_builder.agents.parser_agent import ParserAgent
from resume_builder.models.agent import AgentState, TokenUsage
from resume_builder.models.optimizer import OptimizedResume
from resume_builder.models.orchestrator import FinalResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from resume_builder.models.match import JobDescription, MatchReport


class OrchestratorAgent:
    """Coordinates the multi-agent resume optimisation workflow.

    The orchestrator is NOT itself a ``BaseAgent`` — it never calls Claude
    directly. Instead it holds references to three specialist agents and
    drives them in sequence, aggregating their outputs and token usage into
    a single ``FinalResult``.

    Failure handling:
    - Parser or Matcher failure: re-raises ``ParseError`` (pipeline cannot
      continue without a parsed resume or match report).
    - Optimizer failure: returns a partial ``FinalResult`` with an empty
      ``OptimizedResume`` and the error description in ``errors``.

    Args:
        parser: Pre-built ``ParserAgent``. Created from ``**kwargs`` if omitted.
        matcher: Pre-built ``MatcherAgent``. Created from ``**kwargs`` if omitted.
        optimizer: Pre-built ``OptimizerAgent``. Created from ``**kwargs`` if omitted.
        **kwargs: Forwarded to sub-agent constructors when they are not
            explicitly provided (e.g. ``client``, ``model``, ``max_tokens``).
    """

    def __init__(
        self,
        parser: ParserAgent | None = None,
        matcher: MatcherAgent | None = None,
        optimizer: OptimizerAgent | None = None,
        **kwargs: Any,
    ) -> None:
        self.parser: ParserAgent = parser or ParserAgent(**kwargs)
        self.matcher: MatcherAgent = matcher or MatcherAgent(**kwargs)
        self.optimizer: OptimizerAgent = optimizer or OptimizerAgent(**kwargs)
        self.state: AgentState = AgentState(step="idle")

    async def run(
        self,
        linkedin_data: dict[str, str],
        job: JobDescription,
        on_progress: Callable[[str], None] | None = None,
        approval_callback: Callable[[MatchReport], bool] | None = None,
    ) -> FinalResult:
        """Execute the full optimisation pipeline and return the final result.

        Runs parser → matcher → (optional approval) → optimizer in sequence.
        Token usage is aggregated from all three agents into ``FinalResult``.

        Args:
            linkedin_data: Mapping of CSV type to raw CSV content, forwarded
                to ``ParserAgent.parse()``.
            job: Target job description for matching and optimisation.
            on_progress: Optional callback invoked with step names
                ``"parsing"``, ``"matching"``, ``"optimizing"``, and
                ``"complete"`` as each step begins or finishes.
            approval_callback: Optional callback invoked with the
                ``MatchReport`` after matching. If it returns ``False``,
                the optimizer step is skipped and the result contains an
                empty ``OptimizedResume`` with an error note.

        Returns:
            ``FinalResult`` with the optimised resume, match report, aggregated
            token usage, and any non-fatal error messages.

        Raises:
            ParseError: If the parser or matcher step fails (pipeline cannot
                continue without a valid resume or match report).
        """
        errors: list[str] = []

        # --- Step 1: Parsing ---
        self.state.step = "parsing"
        if on_progress:
            on_progress("parsing")
        resume = await self.parser.parse(linkedin_data)

        # --- Step 2: Matching ---
        self.state.step = "matching"
        if on_progress:
            on_progress("matching")
        match = await self.matcher.analyze(resume, job)

        # --- Step 3: Optional approval gate ---
        if approval_callback is not None and not approval_callback(match):
            errors.append("Optimization skipped: approval rejected by approval_callback")
            return FinalResult(
                resume=OptimizedResume(),
                match=match,
                token_usage=self._aggregate_token_usage(),
                errors=errors,
            )

        # --- Step 4: Optimisation (graceful failure) ---
        self.state.step = "optimizing"
        if on_progress:
            on_progress("optimizing")

        optimized: OptimizedResume
        try:
            optimized = await self.optimizer.optimize(resume, job, match)
        except Exception as exc:
            errors.append(f"Optimizer step failed: {exc}")
            optimized = OptimizedResume()

        # --- Complete ---
        self.state.step = "complete"
        if on_progress:
            on_progress("complete")

        return FinalResult(
            resume=optimized,
            match=match,
            token_usage=self._aggregate_token_usage(),
            errors=errors,
        )

    def get_usage_report(self) -> dict[str, Any]:
        """Return a per-agent and total token usage breakdown.

        Returns:
            Dict with keys ``"parser"``, ``"matcher"``, ``"optimizer"``,
            and ``"total"``, each mapping to a token usage dict containing
            ``input_tokens``, ``output_tokens``, ``total_tokens``, and
            ``estimated_cost``.
        """
        total = self._aggregate_token_usage()
        return {
            "parser": self.parser.token_usage.model_dump(),
            "matcher": self.matcher.token_usage.model_dump(),
            "optimizer": self.optimizer.token_usage.model_dump(),
            "total": total.model_dump(),
        }

    def _aggregate_token_usage(self) -> TokenUsage:
        """Sum token usage across all three sub-agents.

        Returns:
            A new ``TokenUsage`` instance with combined token counts.
        """
        total = TokenUsage()
        total.add(self.parser.token_usage)
        total.add(self.matcher.token_usage)
        total.add(self.optimizer.token_usage)
        return total

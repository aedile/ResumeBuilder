"""Optimizer Agent — improves resume content via Claude tool_use.

The OptimizerAgent sends a resume, job description, and match report to
Claude along with four specialised tools (rewrite_bullet, generate_summary,
suggest_edits, verify_facts). Claude calls these tools as needed, then
returns a JSON object that is validated and converted into an
``OptimizedResume`` instance.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.tools.optimization import (
    GENERATE_SUMMARY_TOOL,
    REWRITE_BULLET_TOOL,
    SUGGEST_EDITS_TOOL,
    VERIFY_FACTS_TOOL,
    generate_summary,
    rewrite_bullet,
    suggest_edits,
    verify_facts,
)
from resume_builder.exceptions import ParseError
from resume_builder.models.optimizer import OptimizedResume

if TYPE_CHECKING:
    from resume_builder.models.match import JobDescription, MatchReport
    from resume_builder.models.resume import Resume


class OptimizerAgent(BaseAgent):
    """Specialist agent that improves resume content for a target job.

    On initialisation, all four optimization tools are registered so that
    Claude can call them during the conversation. The ``optimize`` method
    sends the resume, job description, and match report, handles the full
    tool-use cycle via the base class, and converts the model's final JSON
    response into a validated ``OptimizedResume``.

    Class Attributes:
        SYSTEM_PROMPT: Instruction text forwarded to Claude on every API call.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert resume content optimizer. Your job is to improve resume "
        "content to better match a target job description while preserving the "
        "candidate's authentic voice and never fabricating facts.\n\n"
        "You have four tools available:\n"
        "- rewrite_bullet: Improve individual bullet points with action verbs and "
        "metrics\n"
        "- generate_summary: Create a tailored professional summary\n"
        "- suggest_edits: Recommend content changes based on job requirements\n"
        "- verify_facts: Ensure all claims are grounded in the source resume data\n\n"
        "CRITICAL RULES:\n"
        "1. NEVER invent facts, numbers, or experiences not present in the source resume\n"
        "2. Always use verify_facts before including any specific claim\n"
        "3. Preserve the candidate's authentic voice\n\n"
        "Use these tools to analyse and improve the resume, then respond with a single "
        "JSON object matching the OptimizedResume schema:\n"
        "{\n"
        '  "summary": "<tailored professional summary string or null>",\n'
        '  "optimized_bullets": {"<position title>": ["<bullet 1>", ...]},\n'
        '  "changes": ["<description of change 1>", ...]\n'
        "}\n\n"
        "Return ONLY the JSON object — no markdown, no explanation, no code fences."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise OptimizerAgent and register all optimization tools.

        Args:
            **kwargs: Forwarded to ``BaseAgent.__init__`` (client, model,
                max_tokens, timeout, max_retries).
        """
        super().__init__(**kwargs)
        self.system_prompt = self.SYSTEM_PROMPT
        self.register_tool(REWRITE_BULLET_TOOL, rewrite_bullet)
        self.register_tool(GENERATE_SUMMARY_TOOL, generate_summary)
        self.register_tool(SUGGEST_EDITS_TOOL, suggest_edits)
        self.register_tool(VERIFY_FACTS_TOOL, verify_facts)

    async def optimize(
        self,
        resume: Resume,
        job: JobDescription,
        match: MatchReport,
    ) -> OptimizedResume:
        """Optimize resume content for a target job using match insights.

        Sends the resume, job description, and match report to Claude, which
        uses the registered tools to rewrite bullets, generate a tailored
        summary, and verify all claims. The agent's final JSON response is
        validated and returned as an ``OptimizedResume``.

        Args:
            resume: Source resume data to optimize.
            job: Target job description.
            match: Prior match analysis with gaps and recommendations.

        Returns:
            Validated ``OptimizedResume`` with improved summary, bullets,
            and a change log.

        Raises:
            ParseError: If the API response is not valid JSON or does not
                conform to the ``OptimizedResume`` schema.
        """
        gaps_text = ", ".join(match.gaps) if match.gaps else "none identified"
        recommendations_text = "; ".join(match.recommendations) if match.recommendations else "none"

        prompt = (
            f"Optimize the following resume for the target job. "
            f"Return an OptimizedResume JSON.\n\n"
            f"Job Title: {job.title}\n"
            f"Job Description:\n{job.description}\n\n"
            f"Match Score: {match.overall_score}/100\n"
            f"Skill Gaps: {gaps_text}\n"
            f"Recommendations: {recommendations_text}\n\n"
            f"Resume:\n{resume.model_dump_json(indent=2)}"
        )

        response = await self.send_message(prompt)

        try:
            result_data: dict[str, Any] = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"OptimizerAgent returned non-JSON response: {exc}\n"
                f"Response was: {response.content[:200]}"
            ) from exc

        try:
            return OptimizedResume.model_validate(result_data)
        except (ValidationError, TypeError) as exc:
            raise ParseError(
                f"OptimizerAgent response does not match OptimizedResume schema: {exc}"
            ) from exc

"""Matcher Agent — scores resume-to-job fit via Claude tool_use.

The MatcherAgent sends a resume and job description to Claude along with
four specialised tools (extract_requirements, score_match, identify_gaps,
rank_experience). Claude calls these tools as needed, then returns a JSON
object that is validated and converted into a ``MatchReport`` instance.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.tools.matching import (
    EXTRACT_REQUIREMENTS_TOOL,
    IDENTIFY_GAPS_TOOL,
    RANK_EXPERIENCE_TOOL,
    SCORE_MATCH_TOOL,
    extract_requirements,
    identify_gaps,
    rank_experience,
    score_match,
)
from resume_builder.exceptions import ParseError
from resume_builder.models.match import JobDescription, MatchReport

if TYPE_CHECKING:
    from resume_builder.models.resume import Resume


class MatcherAgent(BaseAgent):
    """Specialist agent that scores how well a resume matches a job description.

    On initialisation, all four matching tools are registered so that Claude
    can call them during the conversation. The ``analyze`` method sends both
    resume and job data, handles the full tool-use cycle via the base class,
    and converts the model's final JSON response into a validated
    ``MatchReport``.

    Class Attributes:
        SYSTEM_PROMPT: Instruction text forwarded to Claude on every API call.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert resume-to-job matcher. Your job is to analyze a resume "
        "and a job description, then produce a detailed match report.\n\n"
        "You have four tools available:\n"
        "- extract_requirements: Parse required skills, experience, and education "
        "from a job description\n"
        "- score_match: Calculate a 0-100 match score between resume skills and "
        "required skills\n"
        "- identify_gaps: Find skills required by the job that the resume is missing\n"
        "- rank_experience: Rank resume positions by relevance to the job keywords\n\n"
        "Use these tools to analyse the provided data, then respond with a single "
        "JSON object matching the MatchReport schema:\n"
        "{\n"
        '  "overall_score": <int 0-100>,\n'
        '  "section_scores": {"skills": <int>, "experience": <int>},\n'
        '  "gaps": [<missing skill strings>],\n'
        '  "recommendations": [<improvement suggestion strings>],\n'
        '  "ranked_positions": [<position title strings ordered by relevance>]\n'
        "}\n\n"
        "Return ONLY the JSON object — no markdown, no explanation, no code fences."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise MatcherAgent and register all matching tools.

        Args:
            **kwargs: Forwarded to ``BaseAgent.__init__`` (client, model,
                max_tokens, timeout, max_retries).
        """
        super().__init__(**kwargs)
        self.system_prompt = self.SYSTEM_PROMPT
        self.register_tool(EXTRACT_REQUIREMENTS_TOOL, extract_requirements)
        self.register_tool(SCORE_MATCH_TOOL, score_match)
        self.register_tool(IDENTIFY_GAPS_TOOL, identify_gaps)
        self.register_tool(RANK_EXPERIENCE_TOOL, rank_experience)

    async def analyze(self, resume: Resume, job: JobDescription) -> MatchReport:
        """Analyse resume-to-job fit and return a structured MatchReport.

        Sends both the resume and job description to Claude, which uses the
        registered tools to extract requirements, score matches, identify gaps,
        and rank positions. The agent's final JSON response is validated and
        returned as a ``MatchReport``.

        Args:
            resume: Parsed resume data to evaluate.
            job: Target job description to match against.

        Returns:
            Validated ``MatchReport`` with overall score, section scores, gaps,
            recommendations, and ranked positions.

        Raises:
            ParseError: If the API response is not valid JSON or does not
                conform to the ``MatchReport`` schema.
        """
        prompt = (
            f"Analyze the following resume against the job description and "
            f"return a MatchReport JSON.\n\n"
            f"Job Title: {job.title}\n"
            f"Job Description:\n{job.description}\n\n"
            f"Resume:\n{resume.model_dump_json(indent=2)}"
        )

        response = await self.send_message(prompt)

        try:
            report_data: dict[str, Any] = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"MatcherAgent returned non-JSON response: {exc}\n"
                f"Response was: {response.content[:200]}"
            ) from exc

        try:
            return MatchReport.model_validate(report_data)
        except (ValidationError, TypeError) as exc:
            raise ParseError(
                f"MatcherAgent response does not match MatchReport schema: {exc}"
            ) from exc

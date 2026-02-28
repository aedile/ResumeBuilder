"""Parser Agent — structures LinkedIn export data via Claude tool_use.

The ParserAgent sends LinkedIn CSV content to Claude along with four
specialised tools (parse_csv, normalize_dates, extract_implicit_skills,
validate_data). Claude calls these tools as needed, then returns a JSON
object that is validated and converted into a ``Resume`` instance.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.tools.parsing import (
    EXTRACT_IMPLICIT_SKILLS_TOOL,
    NORMALIZE_DATES_TOOL,
    PARSE_CSV_TOOL,
    VALIDATE_DATA_TOOL,
    extract_implicit_skills,
    normalize_dates,
    parse_csv,
    validate_data,
)
from resume_builder.exceptions import ParseError
from resume_builder.models.resume import Resume


class ParserAgent(BaseAgent):
    """Specialist agent that structures LinkedIn CSV exports into a Resume.

    On initialisation, all four parsing tools are registered so that Claude
    can call them during the conversation. The ``parse`` method sends the
    LinkedIn data, handles the full tool-use cycle via the base class, and
    converts the model's final JSON response into a validated ``Resume``.

    Class Attributes:
        SYSTEM_PROMPT: Instruction text forwarded to Claude on every API call.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert LinkedIn data parser. Your job is to analyze LinkedIn "
        "CSV export data and structure it into a complete resume JSON object.\n\n"
        "You have four tools available:\n"
        "- parse_csv: Read and parse CSV content from any LinkedIn export file\n"
        "- normalize_dates: Convert date strings to YYYY-MM format\n"
        "- extract_implicit_skills: Find technology skills mentioned in text\n"
        "- validate_data: Check that required fields are present\n\n"
        "Process the provided LinkedIn data using these tools as needed, then "
        "respond with a single JSON object matching the Resume schema:\n"
        "{\n"
        '  "profile": {\n'
        '    "first_name": "string (required)",\n'
        '    "last_name": "string (required)",\n'
        '    "headline": "string (required)",\n'
        '    "summary": "string or null",\n'
        '    "location": "string or null",\n'
        '    "industry": "string or null"\n'
        "  },\n"
        '  "positions": [...],\n'
        '  "skills": [...],\n'
        '  "education": [...]\n'
        "}\n\n"
        "Return ONLY the JSON object — no markdown, no explanation, no code fences."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise ParserAgent and register all parsing tools.

        Args:
            **kwargs: Forwarded to ``BaseAgent.__init__`` (client, model,
                max_tokens, timeout, max_retries).
        """
        super().__init__(**kwargs)
        self.system_prompt = self.SYSTEM_PROMPT
        self.register_tool(PARSE_CSV_TOOL, parse_csv)
        self.register_tool(NORMALIZE_DATES_TOOL, normalize_dates)
        self.register_tool(EXTRACT_IMPLICIT_SKILLS_TOOL, extract_implicit_skills)
        self.register_tool(VALIDATE_DATA_TOOL, validate_data)

    async def parse(self, linkedin_data: dict[str, str]) -> Resume:
        """Parse LinkedIn CSV data into a structured Resume object.

        Sends the LinkedIn export data to Claude, which uses the registered
        tools to parse and normalize the CSVs. The agent returns the final
        JSON response as a validated ``Resume`` instance.

        Args:
            linkedin_data: Mapping of CSV type to raw CSV content string,
                e.g. ``{"profile": "First Name,...", "positions": "..."}``.

        Returns:
            Parsed and validated ``Resume`` instance.

        Raises:
            ParseError: If the API response is not valid JSON or does not
                conform to the ``Resume`` schema.
        """
        prompt = (
            "Parse the following LinkedIn export data and return a Resume JSON:\n\n"
            + json.dumps(linkedin_data, indent=2)
        )

        response = await self.send_message(prompt)

        try:
            resume_data: dict[str, Any] = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"ParserAgent returned non-JSON response: {exc}\n"
                f"Response was: {response.content[:200]}"
            ) from exc

        try:
            return Resume.model_validate(resume_data)
        except (ValidationError, TypeError) as exc:
            raise ParseError(f"ParserAgent response does not match Resume schema: {exc}") from exc

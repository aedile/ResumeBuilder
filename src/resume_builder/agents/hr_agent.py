"""HR Review Agent — evaluates resume text for grammar, formatting, and professional tone.

The HRAgent sends plain text resume content to Claude along with four specialised
tools (check_grammar, validate_formatting, assess_professionalism, detect_placeholders).
Claude calls these tools as needed, then returns a JSON object that is validated
and converted into an ``HRReport`` instance.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.tools.review_hr import (
    ASSESS_PROFESSIONALISM_TOOL,
    CHECK_GRAMMAR_TOOL,
    DETECT_PLACEHOLDERS_TOOL,
    VALIDATE_FORMATTING_TOOL,
    assess_professionalism,
    check_grammar,
    detect_placeholders,
    validate_formatting,
)
from resume_builder.exceptions import ParseError
from resume_builder.models.hr import HRReport


class HRAgent(BaseAgent):
    """Specialist agent that evaluates resume text for HR-facing quality issues.

    On initialisation, all four HR review tools are registered so that Claude
    can call them during the conversation. The ``review`` method sends the
    resume plain text, handles the full tool-use cycle via the base class, and
    converts the model's final JSON response into a validated ``HRReport``.

    Class Attributes:
        SYSTEM_PROMPT: Instruction text forwarded to Claude on every API call.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert HR resume reviewer. Your job is to evaluate plain text "
        "resume content for grammar, formatting consistency, professional tone, and "
        "the presence of leftover template placeholder text.\n\n"
        "You have four tools available:\n"
        "- check_grammar: Scan for double spaces, sentences starting lowercase after "
        "a period, and weak phrases ('responsible for', 'helped with'). Returns "
        "has_issues (bool) and issues (list). Set the report's has_grammar_issues "
        "field to the value returned by this tool.\n"
        "- validate_formatting: Detect mixed date formats (e.g. 'January 2020' "
        "alongside '01/2020'). Returns is_consistent (bool) and issues (list). "
        "Set the report's is_formatting_consistent field from this tool.\n"
        "- assess_professionalism: Evaluate tone by checking for first-person "
        "pronouns, contractions, vague language, and weak phrasing. Returns "
        "professionalism_score (int 0-100), issues (list), and suggestions (list). "
        "Use the score directly in the report. Scores below 70 indicate issues "
        "that should be surfaced to the candidate.\n"
        "- detect_placeholders: Search for Lorem ipsum, XXX, TODO/TBD, bracket "
        "placeholders ([Name], [Company]), and example.com email addresses. "
        "Returns has_placeholders (bool) and placeholders_found (list). Set "
        "the report's has_placeholders field from this tool.\n\n"
        "IMPORTANT — de-duplication: check_grammar and assess_professionalism "
        "both flag weak phrases. If both tools report the same phrase, include it "
        "only once in the final issues list. Do not surface duplicate feedback.\n\n"
        "Use these tools to analyse the provided resume text, then respond with a "
        "single JSON object matching the HRReport schema:\n"
        "{\n"
        '  "professionalism_score": <int 0-100 from assess_professionalism>,\n'
        '  "has_grammar_issues": <bool from check_grammar>,\n'
        '  "is_formatting_consistent": <bool from validate_formatting>,\n'
        '  "has_placeholders": <bool from detect_placeholders>,\n'
        '  "issues": [<de-duplicated issue strings from all tools>],\n'
        '  "suggestions": [<improvement strings from assess_professionalism and your analysis>]\n'
        "}\n\n"
        "Return ONLY the JSON object — no markdown, no explanation, no code fences."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise HRAgent and register all HR review tools.

        Args:
            **kwargs: Forwarded to ``BaseAgent.__init__`` (client, model,
                max_tokens, timeout, max_retries).
        """
        super().__init__(**kwargs)
        self.system_prompt = self.SYSTEM_PROMPT
        self.register_tool(CHECK_GRAMMAR_TOOL, check_grammar)
        self.register_tool(VALIDATE_FORMATTING_TOOL, validate_formatting)
        self.register_tool(ASSESS_PROFESSIONALISM_TOOL, assess_professionalism)
        self.register_tool(DETECT_PLACEHOLDERS_TOOL, detect_placeholders)

    async def review(self, text: str) -> HRReport:
        """Review plain text resume content and return a structured HRReport.

        Sends the text to Claude, which uses the registered tools to check
        grammar, validate date formatting, assess professional tone, and detect
        placeholder text. The agent's final JSON response is validated and
        returned as an ``HRReport``.

        Args:
            text: Plain text content of the resume to evaluate.

        Returns:
            Validated ``HRReport`` with professionalism score, boolean quality
            flags, aggregated issues, and improvement suggestions.

        Raises:
            ParseError: If the API response is not valid JSON or does not
                conform to the ``HRReport`` schema.
        """
        prompt = (
            "Review the following plain text resume for grammar, date formatting "
            "consistency, professional tone, and placeholder text. Use the available "
            "tools to analyse each aspect, then return an HRReport JSON.\n\n"
            f"Resume Text:\n{text}"
        )

        response = await self.send_message(prompt)

        try:
            report_data: dict[str, Any] = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"HRAgent returned non-JSON response: {exc}\nResponse was: {response.content[:200]}"
            ) from exc

        try:
            return HRReport.model_validate(report_data)
        except (ValidationError, TypeError) as exc:
            raise ParseError(f"HRAgent response does not match HRReport schema: {exc}") from exc

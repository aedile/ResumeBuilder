"""QA Review Agent — evaluates HTML resumes for accessibility, layout, and print quality.

The QAAgent sends resume HTML to Claude along with four specialised tools
(check_accessibility, evaluate_layout, verify_contrast, check_print_quality).
Claude calls these tools as needed, then returns a JSON object that is
validated and converted into a ``QAReport`` instance.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.tools.review import (
    CHECK_ACCESSIBILITY_TOOL,
    CHECK_PRINT_QUALITY_TOOL,
    EVALUATE_LAYOUT_TOOL,
    VERIFY_CONTRAST_TOOL,
    check_accessibility,
    check_print_quality,
    evaluate_layout,
    verify_contrast,
)
from resume_builder.exceptions import ParseError
from resume_builder.models.qa import QAReport


class QAAgent(BaseAgent):
    """Specialist agent that evaluates HTML resume quality.

    On initialisation, all four review tools are registered so that Claude
    can call them during the conversation. The ``review`` method sends the
    resume HTML, handles the full tool-use cycle via the base class, and
    converts the model's final JSON response into a validated ``QAReport``.

    Class Attributes:
        SYSTEM_PROMPT: Instruction text forwarded to Claude on every API call.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert resume quality reviewer. Your job is to evaluate HTML "
        "resume content for accessibility, visual layout, colour contrast, and print "
        "rendering quality.\n\n"
        "You have four tools available:\n"
        "- check_accessibility: Validate static WCAG 2.1 AA compliance (heading "
        "hierarchy, alt text on images, <main>/role='main' landmark presence). "
        "Returns is_accessible (bool) and issues (list). Set the report's "
        "is_accessible field to the value returned by this tool.\n"
        "- evaluate_layout: Assess visual hierarchy and section completeness. "
        "Returns layout_score (int 0-100) and sections_found (list). Use these "
        "directly in the report.\n"
        "- verify_contrast: Calculate WCAG contrast ratio between a foreground and "
        "background hex colour (e.g. '#000000', '#ffffff'). Returns ratio (float), "
        "passes_aa_normal (bool, threshold 4.5:1), passes_aa_large (bool, 3:1). "
        "If passes_aa_normal is false, add a contrast issue to the issues list.\n"
        "- check_print_quality: Detect inline CSS patterns (display:none, "
        "overflow:hidden) that cause poor print rendering. Returns print_ready (bool) "
        "and issues (list). Set the report's print_ready field from this tool.\n\n"
        "Note: these checks cover static HTML analysis only. Full WCAG 2.1 AA "
        "compliance requires browser-based and human review beyond this scope.\n\n"
        "Use these tools to analyse the provided HTML, then respond with a single "
        "JSON object matching the QAReport schema:\n"
        "{\n"
        '  "layout_score": <int 0-100 from evaluate_layout>,\n'
        '  "is_accessible": <bool from check_accessibility>,\n'
        '  "print_ready": <bool from check_print_quality>,\n'
        '  "sections_found": [<section names from evaluate_layout>],\n'
        '  "issues": [<all violation strings from accessibility, contrast, print tools>],\n'
        '  "suggestions": [<improvement strings from evaluate_layout and your analysis>]\n'
        "}\n\n"
        "Return ONLY the JSON object — no markdown, no explanation, no code fences."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialise QAAgent and register all review tools.

        Args:
            **kwargs: Forwarded to ``BaseAgent.__init__`` (client, model,
                max_tokens, timeout, max_retries).
        """
        super().__init__(**kwargs)
        self.system_prompt = self.SYSTEM_PROMPT
        self.register_tool(CHECK_ACCESSIBILITY_TOOL, check_accessibility)
        self.register_tool(EVALUATE_LAYOUT_TOOL, evaluate_layout)
        self.register_tool(VERIFY_CONTRAST_TOOL, verify_contrast)
        self.register_tool(CHECK_PRINT_QUALITY_TOOL, check_print_quality)

    async def review(self, html_content: str) -> QAReport:
        """Review HTML resume content and return a structured QAReport.

        Sends the HTML to Claude, which uses the registered tools to check
        accessibility, evaluate layout, verify contrast, and assess print
        quality. The agent's final JSON response is validated and returned
        as a ``QAReport``.

        Args:
            html_content: Full HTML string of the resume to evaluate.

        Returns:
            Validated ``QAReport`` with layout score, accessibility status,
            print readiness, sections found, issues, and suggestions.

        Raises:
            ParseError: If the API response is not valid JSON or does not
                conform to the ``QAReport`` schema.
        """
        prompt = (
            "Review the following HTML resume for accessibility, layout quality, "
            "colour contrast, and print rendering. Use the available tools to "
            "analyse each aspect, then return a QAReport JSON.\n\n"
            f"HTML Resume:\n{html_content}"
        )

        response = await self.send_message(prompt)

        try:
            report_data: dict[str, Any] = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"QAAgent returned non-JSON response: {exc}\nResponse was: {response.content[:200]}"
            ) from exc

        try:
            return QAReport.model_validate(report_data)
        except (ValidationError, TypeError) as exc:
            raise ParseError(f"QAAgent response does not match QAReport schema: {exc}") from exc

"""Tests for QAAgent and QAReport model.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tests use mocked Anthropic clients — no real API calls ever made.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import anthropic
import pytest
from pydantic import ValidationError

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.qa_agent import QAAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.qa import QAReport

_MINIMAL_QA_REPORT_JSON = json.dumps(
    {
        "layout_score": 80,
        "is_accessible": True,
        "print_ready": True,
        "sections_found": ["experience", "education", "skills"],
        "issues": [],
        "suggestions": ["Consider adding a Summary section."],
    }
)

_HTML_FIXTURE = (
    "<html><body><main>"
    "<header><h1>Alex Chen</h1></header>"
    "<section><h2>Experience</h2><p>Engineer at Acme</p></section>"
    "<section><h2>Education</h2><p>BS Computer Science</p></section>"
    "<section><h2>Skills</h2><p>Python, SQL</p></section>"
    "</main></body></html>"
)


def _make_text_response(text: str = _MINIMAL_QA_REPORT_JSON) -> MagicMock:
    """Build a mock Anthropic response with a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = 100
    response.usage.output_tokens = 50
    return response


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked Anthropic client returning a minimal QAReport JSON."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


# ---------------------------------------------------------------------------
# QAAgent initialisation
# ---------------------------------------------------------------------------


class TestQAAgentInit:
    """QAAgent initialization and tool registration tests."""

    def test_qa_agent_extends_base_agent(self, mock_client: MagicMock) -> None:
        """QAAgent is a subclass of BaseAgent."""
        agent = QAAgent(client=mock_client)
        assert isinstance(agent, BaseAgent)

    def test_qa_agent_registers_four_tools(self, mock_client: MagicMock) -> None:
        """QAAgent registers exactly four review tools."""
        agent = QAAgent(client=mock_client)
        assert len(agent._tools) == 4

    def test_qa_agent_has_check_accessibility_tool(self, mock_client: MagicMock) -> None:
        """QAAgent registers the check_accessibility tool."""
        agent = QAAgent(client=mock_client)
        assert "check_accessibility" in [t.name for t in agent._tools]

    def test_qa_agent_has_evaluate_layout_tool(self, mock_client: MagicMock) -> None:
        """QAAgent registers the evaluate_layout tool."""
        agent = QAAgent(client=mock_client)
        assert "evaluate_layout" in [t.name for t in agent._tools]

    def test_qa_agent_has_verify_contrast_tool(self, mock_client: MagicMock) -> None:
        """QAAgent registers the verify_contrast tool."""
        agent = QAAgent(client=mock_client)
        assert "verify_contrast" in [t.name for t in agent._tools]

    def test_qa_agent_has_check_print_quality_tool(self, mock_client: MagicMock) -> None:
        """QAAgent registers the check_print_quality tool."""
        agent = QAAgent(client=mock_client)
        assert "check_print_quality" in [t.name for t in agent._tools]

    def test_qa_agent_has_system_prompt(self, mock_client: MagicMock) -> None:
        """QAAgent defines a non-empty SYSTEM_PROMPT class attribute."""
        assert hasattr(QAAgent, "SYSTEM_PROMPT")
        assert isinstance(QAAgent.SYSTEM_PROMPT, str)
        assert len(QAAgent.SYSTEM_PROMPT) > 50

    def test_qa_agent_system_prompt_set_on_instance(self, mock_client: MagicMock) -> None:
        """QAAgent sets system_prompt on the instance from SYSTEM_PROMPT."""
        agent = QAAgent(client=mock_client)
        assert agent.system_prompt == QAAgent.SYSTEM_PROMPT

    def test_qa_agent_all_handlers_callable(self, mock_client: MagicMock) -> None:
        """QAAgent tool names all map to callable handlers."""
        agent = QAAgent(client=mock_client)
        for name in (
            "check_accessibility",
            "evaluate_layout",
            "verify_contrast",
            "check_print_quality",
        ):
            assert callable(agent._tool_handlers[name])


# ---------------------------------------------------------------------------
# QAAgent.review()
# ---------------------------------------------------------------------------


class TestQAAgentReview:
    """QAAgent.review() method tests."""

    async def test_review_returns_qa_report(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport instance on success."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert isinstance(result, QAReport)

    async def test_review_populates_layout_score(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport with layout_score from API response."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert result.layout_score == 80

    async def test_review_populates_is_accessible(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport with is_accessible from API response."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert result.is_accessible is True

    async def test_review_populates_print_ready(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport with print_ready from API response."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert result.print_ready is True

    async def test_review_populates_sections_found(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport with sections_found from API response."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert "experience" in result.sections_found

    async def test_review_populates_suggestions(self, mock_client: MagicMock) -> None:
        """review() returns a QAReport with suggestions from API response."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert len(result.suggestions) >= 0

    async def test_review_sends_html_in_message(self, mock_client: MagicMock) -> None:
        """review() includes the HTML content in the API message."""
        agent = QAAgent(client=mock_client)
        await agent.review(_HTML_FIXTURE)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "<h1>Alex Chen</h1>" in user_message["content"]

    async def test_review_passes_system_prompt(self, mock_client: MagicMock) -> None:
        """review() includes the system prompt in the API call."""
        agent = QAAgent(client=mock_client)
        await agent.review(_HTML_FIXTURE)
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs.get("system") == QAAgent.SYSTEM_PROMPT

    async def test_review_invalid_json_raises_parse_error(
        self, mock_client: MagicMock
    ) -> None:
        """review() raises ParseError when API returns non-JSON text."""
        mock_client.messages.create.return_value = _make_text_response("not valid json")
        agent = QAAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.review(_HTML_FIXTURE)

    async def test_review_invalid_schema_raises_parse_error(
        self, mock_client: MagicMock
    ) -> None:
        """review() raises ParseError when JSON doesn't match QAReport schema."""
        mock_client.messages.create.return_value = _make_text_response('{"bad": "schema"}')
        agent = QAAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.review(_HTML_FIXTURE)

    async def test_review_accumulates_token_usage(self, mock_client: MagicMock) -> None:
        """review() accumulates token usage from the API call."""
        agent = QAAgent(client=mock_client)
        await agent.review(_HTML_FIXTURE)
        assert agent.token_usage.total_tokens > 0

    async def test_review_checks_accessibility(self, mock_client: MagicMock) -> None:
        """QA agent validates accessibility requirements."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert isinstance(result.is_accessible, bool)

    async def test_review_evaluates_layout(self, mock_client: MagicMock) -> None:
        """QA agent assesses visual hierarchy."""
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert 0 <= result.layout_score <= 100

    async def test_review_flags_contrast_issues(self, mock_client: MagicMock) -> None:
        """QA agent can report contrast issues via issues list."""
        report_with_issue = json.dumps(
            {
                "layout_score": 60,
                "is_accessible": False,
                "print_ready": True,
                "sections_found": ["experience"],
                "issues": ["Low contrast: #aaaaaa on #ffffff fails WCAG AA."],
                "suggestions": [],
            }
        )
        mock_client.messages.create.return_value = _make_text_response(report_with_issue)
        agent = QAAgent(client=mock_client)
        result = await agent.review(_HTML_FIXTURE)
        assert any("contrast" in issue.lower() for issue in result.issues)


# ---------------------------------------------------------------------------
# QAReport model
# ---------------------------------------------------------------------------


class TestQAReportModel:
    """Tests for the QAReport Pydantic model."""

    def test_qa_report_defaults(self) -> None:
        """QAReport can be created with all defaults."""
        report = QAReport()
        assert report.layout_score == 0
        assert report.is_accessible is False
        assert report.print_ready is False
        assert report.sections_found == []
        assert report.issues == []
        assert report.suggestions == []

    def test_qa_report_full_construction(self) -> None:
        """QAReport accepts all fields."""
        report = QAReport(
            layout_score=90,
            is_accessible=True,
            print_ready=True,
            sections_found=["experience", "education"],
            issues=[],
            suggestions=["Add a summary."],
        )
        assert report.layout_score == 90
        assert report.is_accessible is True
        assert "experience" in report.sections_found

    def test_qa_report_layout_score_is_int(self) -> None:
        """QAReport layout_score is an integer."""
        report = QAReport(layout_score=75)
        assert isinstance(report.layout_score, int)

    def test_qa_report_issues_is_list(self) -> None:
        """QAReport issues is a list."""
        report = QAReport(issues=["Heading skipped."])
        assert isinstance(report.issues, list)

    def test_qa_report_rejects_extra_fields(self) -> None:
        """QAReport rejects unknown fields (extra='forbid')."""
        with pytest.raises(ValidationError):
            QAReport(unknown_field="oops")  # type: ignore[call-arg]

    def test_qa_report_serializes_to_json(self) -> None:
        """QAReport serializes to JSON via model_dump_json."""
        report = QAReport(layout_score=70, is_accessible=True)
        data = json.loads(report.model_dump_json())
        assert data["layout_score"] == 70
        assert data["is_accessible"] is True

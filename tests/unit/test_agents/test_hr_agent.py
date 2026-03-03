"""Tests for HRAgent and HRReport model.

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
from resume_builder.agents.hr_agent import HRAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.hr import HRReport

_MINIMAL_HR_REPORT_JSON = json.dumps(
    {
        "professionalism_score": 85,
        "has_grammar_issues": False,
        "is_formatting_consistent": True,
        "has_placeholders": False,
        "issues": [],
        "suggestions": ["Consider quantifying your achievements with specific metrics."],
    }
)

_TEXT_FIXTURE = (
    "Designed and implemented distributed microservices architecture. "
    "Led cross-functional team of eight engineers from January 2020 to March 2023. "
    "Reduced deployment latency by 40 percent. "
    "Delivered three major product launches on schedule."
)


def _make_text_response(text: str = _MINIMAL_HR_REPORT_JSON) -> MagicMock:
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
    """Mocked Anthropic client returning a minimal HRReport JSON."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


# ---------------------------------------------------------------------------
# HRAgent initialisation
# ---------------------------------------------------------------------------


class TestHRAgentInit:
    """HRAgent initialization and tool registration tests."""

    def test_hr_agent_extends_base_agent(self, mock_client: MagicMock) -> None:
        """HRAgent is a subclass of BaseAgent."""
        agent = HRAgent(client=mock_client)
        assert isinstance(agent, BaseAgent)

    def test_hr_agent_registers_four_tools(self, mock_client: MagicMock) -> None:
        """HRAgent registers exactly four review tools."""
        agent = HRAgent(client=mock_client)
        assert len(agent._tools) == 4

    def test_hr_agent_has_check_grammar_tool(self, mock_client: MagicMock) -> None:
        """HRAgent registers the check_grammar tool."""
        agent = HRAgent(client=mock_client)
        assert "check_grammar" in [t.name for t in agent._tools]

    def test_hr_agent_has_validate_formatting_tool(self, mock_client: MagicMock) -> None:
        """HRAgent registers the validate_formatting tool."""
        agent = HRAgent(client=mock_client)
        assert "validate_formatting" in [t.name for t in agent._tools]

    def test_hr_agent_has_assess_professionalism_tool(self, mock_client: MagicMock) -> None:
        """HRAgent registers the assess_professionalism tool."""
        agent = HRAgent(client=mock_client)
        assert "assess_professionalism" in [t.name for t in agent._tools]

    def test_hr_agent_has_detect_placeholders_tool(self, mock_client: MagicMock) -> None:
        """HRAgent registers the detect_placeholders tool."""
        agent = HRAgent(client=mock_client)
        assert "detect_placeholders" in [t.name for t in agent._tools]

    def test_hr_agent_has_system_prompt(self, mock_client: MagicMock) -> None:
        """HRAgent defines a non-empty SYSTEM_PROMPT class attribute."""
        assert hasattr(HRAgent, "SYSTEM_PROMPT")
        assert isinstance(HRAgent.SYSTEM_PROMPT, str)
        assert len(HRAgent.SYSTEM_PROMPT) > 50

    def test_hr_agent_system_prompt_set_on_instance(self, mock_client: MagicMock) -> None:
        """HRAgent sets system_prompt on the instance from SYSTEM_PROMPT."""
        agent = HRAgent(client=mock_client)
        assert agent.system_prompt == HRAgent.SYSTEM_PROMPT

    def test_hr_agent_all_handlers_callable(self, mock_client: MagicMock) -> None:
        """HRAgent tool names all map to callable handlers."""
        agent = HRAgent(client=mock_client)
        for name in (
            "check_grammar",
            "validate_formatting",
            "assess_professionalism",
            "detect_placeholders",
        ):
            assert callable(agent._tool_handlers[name])


# ---------------------------------------------------------------------------
# HRAgent.review() method tests
# ---------------------------------------------------------------------------


class TestHRAgentReview:
    """HRAgent.review() method tests."""

    async def test_review_returns_hr_report(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport instance on success."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert isinstance(result, HRReport)

    async def test_review_populates_professionalism_score(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport with professionalism_score from API response."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.professionalism_score == 85

    async def test_review_populates_has_grammar_issues(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport with has_grammar_issues from API response."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.has_grammar_issues is False

    async def test_review_populates_is_formatting_consistent(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport with is_formatting_consistent from API response."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.is_formatting_consistent is True

    async def test_review_populates_has_placeholders(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport with has_placeholders from API response."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.has_placeholders is False

    async def test_review_populates_suggestions(self, mock_client: MagicMock) -> None:
        """review() returns an HRReport with suggestions from API response."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert len(result.suggestions) == 1
        assert "metrics" in result.suggestions[0].lower()

    async def test_review_sends_text_in_message(self, mock_client: MagicMock) -> None:
        """review() includes the plain text content in the API message."""
        agent = HRAgent(client=mock_client)
        await agent.review(_TEXT_FIXTURE)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "Designed and implemented" in user_message["content"]

    async def test_review_passes_system_prompt(self, mock_client: MagicMock) -> None:
        """review() includes the system prompt in the API call."""
        agent = HRAgent(client=mock_client)
        await agent.review(_TEXT_FIXTURE)
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs.get("system") == HRAgent.SYSTEM_PROMPT

    async def test_review_invalid_json_raises_parse_error(self, mock_client: MagicMock) -> None:
        """review() raises ParseError when API returns non-JSON text."""
        mock_client.messages.create.return_value = _make_text_response("not valid json")
        agent = HRAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.review(_TEXT_FIXTURE)

    async def test_review_invalid_schema_raises_parse_error(self, mock_client: MagicMock) -> None:
        """review() raises ParseError when JSON doesn't match HRReport schema."""
        mock_client.messages.create.return_value = _make_text_response('{"bad": "schema"}')
        agent = HRAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.review(_TEXT_FIXTURE)

    async def test_review_accumulates_token_usage(self, mock_client: MagicMock) -> None:
        """review() accumulates token usage from the API call."""
        agent = HRAgent(client=mock_client)
        await agent.review(_TEXT_FIXTURE)
        assert agent.token_usage.total_tokens > 0

    async def test_review_checks_grammar(self, mock_client: MagicMock) -> None:
        """HR agent checks grammar and returns a boolean flag."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.has_grammar_issues is False

    async def test_review_validates_dates(self, mock_client: MagicMock) -> None:
        """HR agent validates date formatting consistency."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.is_formatting_consistent is True

    async def test_review_detects_placeholders(self, mock_client: MagicMock) -> None:
        """HR agent reports placeholder detection result."""
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.has_placeholders is False

    async def test_review_reports_grammar_issues_when_present(self, mock_client: MagicMock) -> None:
        """review() surfaces grammar issues from the API response."""
        report_with_grammar = json.dumps(
            {
                "professionalism_score": 65,
                "has_grammar_issues": True,
                "is_formatting_consistent": True,
                "has_placeholders": False,
                "issues": ["Weak phrase detected: 'responsible for'."],
                "suggestions": ["Replace 'responsible for' with an action verb."],
            }
        )
        mock_client.messages.create.return_value = _make_text_response(report_with_grammar)
        agent = HRAgent(client=mock_client)
        result = await agent.review(_TEXT_FIXTURE)
        assert result.has_grammar_issues is True
        assert any("responsible for" in issue.lower() for issue in result.issues)


# ---------------------------------------------------------------------------
# HRReport model
# ---------------------------------------------------------------------------


class TestHRReportModel:
    """Tests for the HRReport Pydantic model."""

    def test_hr_report_defaults(self) -> None:
        """HRReport can be created with all defaults."""
        report = HRReport()
        assert report.professionalism_score == 0
        assert report.has_grammar_issues is False
        assert report.is_formatting_consistent is True
        assert report.has_placeholders is False
        assert report.issues == []
        assert report.suggestions == []

    def test_hr_report_full_construction(self) -> None:
        """HRReport accepts all fields."""
        report = HRReport(
            professionalism_score=90,
            has_grammar_issues=False,
            is_formatting_consistent=True,
            has_placeholders=False,
            issues=[],
            suggestions=["Quantify achievements."],
        )
        assert report.professionalism_score == 90
        assert report.suggestions == ["Quantify achievements."]

    def test_hr_report_score_is_int(self) -> None:
        """HRReport professionalism_score is an integer."""
        report = HRReport(professionalism_score=75)
        assert isinstance(report.professionalism_score, int)

    def test_hr_report_score_rejects_out_of_range(self) -> None:
        """HRReport professionalism_score must be between 0 and 100 inclusive."""
        with pytest.raises(ValidationError):
            HRReport(professionalism_score=-1)
        with pytest.raises(ValidationError):
            HRReport(professionalism_score=101)

    def test_hr_report_issues_is_list(self) -> None:
        """HRReport issues is a list of strings."""
        report = HRReport(issues=["Contraction found: didn't."])
        assert isinstance(report.issues, list)
        assert all(isinstance(i, str) for i in report.issues)

    def test_hr_report_rejects_extra_fields(self) -> None:
        """HRReport rejects unknown fields (extra='forbid')."""
        with pytest.raises(ValidationError):
            HRReport(unknown_field="oops")  # type: ignore[call-arg]

    def test_hr_report_serializes_to_json(self) -> None:
        """HRReport serializes to JSON via model_dump_json."""
        report = HRReport(professionalism_score=80, has_grammar_issues=True)
        data = json.loads(report.model_dump_json())
        assert data["professionalism_score"] == 80
        assert data["has_grammar_issues"] is True

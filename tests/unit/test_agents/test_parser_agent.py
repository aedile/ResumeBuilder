"""Tests for ParserAgent.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tests use mocked Anthropic clients — no real API calls ever made.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import anthropic
import pytest

from resume_builder.agents.base import BaseAgent
from resume_builder.agents.parser_agent import ParserAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.resume import Resume

_MINIMAL_RESUME_JSON = json.dumps(
    {
        "profile": {
            "first_name": "Alex",
            "last_name": "Chen",
            "headline": "Software Engineer",
        },
    }
)


def _make_text_response(text: str = _MINIMAL_RESUME_JSON) -> MagicMock:
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
    """Mocked Anthropic client returning a minimal Resume JSON response."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


class TestParserAgentInit:
    """ParserAgent initialization and tool registration tests."""

    def test_parser_agent_extends_base_agent(self, mock_client: MagicMock) -> None:
        """ParserAgent is a subclass of BaseAgent."""
        agent = ParserAgent(client=mock_client)
        assert isinstance(agent, BaseAgent)

    def test_parser_agent_registers_four_tools(self, mock_client: MagicMock) -> None:
        """ParserAgent registers exactly four parsing tools."""
        agent = ParserAgent(client=mock_client)
        assert len(agent._tools) == 4

    def test_parser_agent_has_parse_csv_tool(self, mock_client: MagicMock) -> None:
        """ParserAgent registers the parse_csv tool."""
        agent = ParserAgent(client=mock_client)
        tool_names = [t.name for t in agent._tools]
        assert "parse_csv" in tool_names

    def test_parser_agent_has_normalize_dates_tool(self, mock_client: MagicMock) -> None:
        """ParserAgent registers the normalize_dates tool."""
        agent = ParserAgent(client=mock_client)
        tool_names = [t.name for t in agent._tools]
        assert "normalize_dates" in tool_names

    def test_parser_agent_has_extract_implicit_skills_tool(self, mock_client: MagicMock) -> None:
        """ParserAgent registers the extract_implicit_skills tool."""
        agent = ParserAgent(client=mock_client)
        tool_names = [t.name for t in agent._tools]
        assert "extract_implicit_skills" in tool_names

    def test_parser_agent_has_validate_data_tool(self, mock_client: MagicMock) -> None:
        """ParserAgent registers the validate_data tool."""
        agent = ParserAgent(client=mock_client)
        tool_names = [t.name for t in agent._tools]
        assert "validate_data" in tool_names

    def test_parser_agent_has_system_prompt(self, mock_client: MagicMock) -> None:
        """ParserAgent defines a non-empty SYSTEM_PROMPT class attribute."""
        assert hasattr(ParserAgent, "SYSTEM_PROMPT")
        assert isinstance(ParserAgent.SYSTEM_PROMPT, str)
        assert len(ParserAgent.SYSTEM_PROMPT) > 50

    def test_parser_agent_tool_handlers_registered(self, mock_client: MagicMock) -> None:
        """ParserAgent tool names map to callable handlers."""
        agent = ParserAgent(client=mock_client)
        for name in ("parse_csv", "normalize_dates", "extract_implicit_skills", "validate_data"):
            assert name in agent._tool_handlers
            assert callable(agent._tool_handlers[name])


class TestParserAgentParse:
    """ParserAgent.parse() method tests."""

    async def test_parse_returns_resume(self, mock_client: MagicMock) -> None:
        """parse() returns a Resume instance on success."""
        agent = ParserAgent(client=mock_client)
        result = await agent.parse({"profile": "First Name,Last Name,Headline\nAlex,Chen,Engineer"})
        assert isinstance(result, Resume)

    async def test_parse_populates_first_name(self, mock_client: MagicMock) -> None:
        """parse() returns a Resume with first_name from API response JSON."""
        agent = ParserAgent(client=mock_client)
        result = await agent.parse({"profile": "csv"})
        assert result.profile.first_name == "Alex"

    async def test_parse_populates_last_name(self, mock_client: MagicMock) -> None:
        """parse() returns a Resume with last_name from API response JSON."""
        agent = ParserAgent(client=mock_client)
        result = await agent.parse({"profile": "csv"})
        assert result.profile.last_name == "Chen"

    async def test_parse_sends_linkedin_data_in_message(self, mock_client: MagicMock) -> None:
        """parse() includes the LinkedIn CSV data in the API message."""
        agent = ParserAgent(client=mock_client)
        await agent.parse({"profile": "csv_content_here"})
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "csv_content_here" in user_message["content"]

    async def test_parse_invalid_json_response_raises_parse_error(
        self, mock_client: MagicMock
    ) -> None:
        """parse() raises ParseError when API returns non-JSON text."""
        mock_client.messages.create.return_value = _make_text_response("not valid json at all")
        agent = ParserAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.parse({"profile": "csv"})

    async def test_parse_invalid_resume_schema_raises_parse_error(
        self, mock_client: MagicMock
    ) -> None:
        """parse() raises ParseError when JSON doesn't match Resume schema."""
        mock_client.messages.create.return_value = _make_text_response('{"wrong_field": "data"}')
        agent = ParserAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.parse({"profile": "csv"})

    async def test_parse_accumulates_token_usage(self, mock_client: MagicMock) -> None:
        """parse() accumulates token usage from the API call."""
        agent = ParserAgent(client=mock_client)
        await agent.parse({"profile": "csv"})
        assert agent.token_usage.total_tokens > 0

    async def test_parse_passes_system_prompt(self, mock_client: MagicMock) -> None:
        """parse() includes the system prompt in the API call."""
        agent = ParserAgent(client=mock_client)
        await agent.parse({"profile": "csv"})
        call_args = mock_client.messages.create.call_args
        assert "system" in call_args.kwargs
        assert call_args.kwargs["system"] == ParserAgent.SYSTEM_PROMPT

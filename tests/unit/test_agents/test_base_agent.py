"""Tests for BaseAgent class.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tests use mocked Anthropic clients — no real API calls ever made.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import anthropic
import httpx
import pytest

from resume_builder.agents.base import BaseAgent
from resume_builder.models.agent import AgentResponse, ToolDefinition


def _make_text_response(text: str = "Test response") -> MagicMock:
    """Build a mock Anthropic message response with a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = 100
    response.usage.output_tokens = 50
    return response


def _make_tool_response(tool_id: str, tool_name: str, tool_input: dict) -> MagicMock:
    """Build a mock Anthropic response that requests a tool call."""
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = tool_name
    block.input = tool_input

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "tool_use"
    response.usage.input_tokens = 80
    response.usage.output_tokens = 30
    return response


def _make_rate_limit_error() -> anthropic.RateLimitError:
    """Construct a minimal RateLimitError for testing retry logic."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 429
    mock_resp.headers = httpx.Headers({})
    mock_resp.request = MagicMock(spec=httpx.Request)
    return anthropic.RateLimitError(
        message="Rate limit exceeded",
        response=mock_resp,
        body={"error": {"type": "rate_limit_error"}},
    )


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked Anthropic client returning a default text response."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


class TestBaseAgentInit:
    """BaseAgent initialisation tests."""

    def test_default_model(self, mock_client: MagicMock) -> None:
        """BaseAgent uses claude-sonnet-4-6 as the default model."""
        agent = BaseAgent(client=mock_client)
        assert agent.model == "claude-sonnet-4-6"

    def test_default_max_tokens(self, mock_client: MagicMock) -> None:
        """BaseAgent defaults to 4096 max_tokens."""
        agent = BaseAgent(client=mock_client)
        assert agent.max_tokens == 4096

    def test_default_timeout(self, mock_client: MagicMock) -> None:
        """BaseAgent defaults to 30.0 second timeout."""
        agent = BaseAgent(client=mock_client)
        assert agent.timeout == 30.0

    def test_starts_with_no_tools(self, mock_client: MagicMock) -> None:
        """BaseAgent starts with an empty tools list."""
        agent = BaseAgent(client=mock_client)
        assert agent._tools == []

    def test_starts_with_empty_history(self, mock_client: MagicMock) -> None:
        """BaseAgent starts with no message history."""
        agent = BaseAgent(client=mock_client)
        assert agent.message_history == []

    def test_starts_with_zero_token_usage(self, mock_client: MagicMock) -> None:
        """BaseAgent starts with zeroed token usage."""
        agent = BaseAgent(client=mock_client)
        assert agent.token_usage.input_tokens == 0
        assert agent.token_usage.output_tokens == 0

    def test_custom_parameters(self, mock_client: MagicMock) -> None:
        """BaseAgent accepts custom model, max_tokens, timeout, max_retries."""
        agent = BaseAgent(
            client=mock_client,
            model="claude-opus-4-6",
            max_tokens=8192,
            timeout=60.0,
            max_retries=5,
        )
        assert agent.model == "claude-opus-4-6"
        assert agent.max_tokens == 8192
        assert agent.timeout == 60.0
        assert agent.max_retries == 5


class TestBaseAgentToolRegistration:
    """Tool registration tests."""

    def test_register_tool_adds_to_list(self, mock_client: MagicMock) -> None:
        """register_tool appends the ToolDefinition to the tools list."""
        agent = BaseAgent(client=mock_client)
        tool_def = ToolDefinition(
            name="my_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}},
        )
        agent.register_tool(tool_def, handler=lambda: "ok")
        assert len(agent._tools) == 1
        assert agent._tools[0].name == "my_tool"

    def test_register_tool_stores_handler(self, mock_client: MagicMock) -> None:
        """register_tool maps tool name to its callable handler."""
        agent = BaseAgent(client=mock_client)
        handler = lambda: "result"  # noqa: E731
        tool_def = ToolDefinition(
            name="echo", description="Echo", input_schema={"type": "object", "properties": {}}
        )
        agent.register_tool(tool_def, handler=handler)
        assert "echo" in agent._tool_handlers
        assert agent._tool_handlers["echo"] is handler

    def test_register_multiple_tools(self, mock_client: MagicMock) -> None:
        """Multiple tools can be registered and all are accessible."""
        agent = BaseAgent(client=mock_client)
        for name in ("tool_a", "tool_b", "tool_c"):
            agent.register_tool(
                ToolDefinition(
                    name=name,
                    description=name,
                    input_schema={"type": "object", "properties": {}},
                ),
                handler=lambda n=name: n,
            )
        assert len(agent._tools) == 3
        assert "tool_a" in agent._tool_handlers
        assert "tool_c" in agent._tool_handlers


class TestBaseAgentSendMessage:
    """send_message behaviour tests."""

    async def test_returns_agent_response(self, mock_client: MagicMock) -> None:
        """send_message returns an AgentResponse instance."""
        agent = BaseAgent(client=mock_client)
        result = await agent.send_message("Hello")
        assert isinstance(result, AgentResponse)

    async def test_response_contains_text(self, mock_client: MagicMock) -> None:
        """AgentResponse.content matches the text returned by the API."""
        mock_client.messages.create.return_value = _make_text_response("Hi there!")
        agent = BaseAgent(client=mock_client)
        result = await agent.send_message("Hello")
        assert result.content == "Hi there!"

    async def test_appends_user_message_to_history(self, mock_client: MagicMock) -> None:
        """send_message adds the user content to message_history."""
        agent = BaseAgent(client=mock_client)
        await agent.send_message("Greetings")
        assert agent.message_history[0] == {"role": "user", "content": "Greetings"}

    async def test_accumulates_token_usage(self, mock_client: MagicMock) -> None:
        """Token usage from each API call is accumulated on the agent."""
        agent = BaseAgent(client=mock_client)
        await agent.send_message("First call")
        await agent.send_message("Second call")
        # mock returns 100 input + 50 output per call
        assert agent.token_usage.input_tokens == 200
        assert agent.token_usage.output_tokens == 100

    async def test_passes_tools_to_api(self, mock_client: MagicMock) -> None:
        """Registered tools are forwarded to the Anthropic API call."""
        agent = BaseAgent(client=mock_client)
        tool_def = ToolDefinition(
            name="my_tool", description="desc", input_schema={"type": "object", "properties": {}}
        )
        agent.register_tool(tool_def, handler=lambda: "ok")
        await agent.send_message("Use a tool")
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "tools" in call_kwargs
        assert call_kwargs["tools"][0]["name"] == "my_tool"

    async def test_executes_tool_call_and_continues(self, mock_client: MagicMock) -> None:
        """When API returns tool_use, agent calls the handler and sends result back."""
        tool_response = _make_tool_response("toolu_01", "echo_tool", {"text": "ping"})
        final_response = _make_text_response("pong received")
        mock_client.messages.create.side_effect = [tool_response, final_response]

        agent = BaseAgent(client=mock_client)
        agent.register_tool(
            ToolDefinition(
                name="echo_tool",
                description="Echo",
                input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            ),
            handler=lambda text: f"echo: {text}",
        )
        result = await agent.send_message("Call echo_tool")
        assert result.content == "pong received"
        assert mock_client.messages.create.call_count == 2

    async def test_tool_result_added_to_history(self, mock_client: MagicMock) -> None:
        """Tool results are added to message_history before the follow-up call."""
        tool_response = _make_tool_response("toolu_01", "echo_tool", {"text": "hi"})
        final_response = _make_text_response("done")
        mock_client.messages.create.side_effect = [tool_response, final_response]

        agent = BaseAgent(client=mock_client)
        agent.register_tool(
            ToolDefinition(
                name="echo_tool",
                description="Echo",
                input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            ),
            handler=lambda text: "result",
        )
        await agent.send_message("Go")
        # history: user msg, assistant tool_use, user tool_result, assistant final
        roles = [m["role"] for m in agent.message_history]
        assert roles.count("user") == 2
        assert roles.count("assistant") == 2

    async def test_unknown_tool_logs_warning(
        self, mock_client: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Unknown tool calls produce a WARNING log entry with the tool name."""
        tool_response = _make_tool_response("toolu_99", "nonexistent_tool", {})
        final_response = _make_text_response("ok")
        mock_client.messages.create.side_effect = [tool_response, final_response]

        agent = BaseAgent(client=mock_client)
        with caplog.at_level(logging.WARNING, logger="resume_builder.agents.base"):
            await agent.send_message("Call unknown tool")

        assert any(
            "nonexistent_tool" in r.message and r.levelno == logging.WARNING for r in caplog.records
        )


class TestBaseAgentRetry:
    """Retry logic tests."""

    async def test_retries_on_rate_limit(self) -> None:
        """send_message retries up to max_retries on RateLimitError."""
        client = MagicMock(spec=anthropic.Anthropic)
        error = _make_rate_limit_error()
        client.messages.create.side_effect = [error, error, _make_text_response("ok")]

        with patch("resume_builder.agents.base.asyncio.sleep"):
            agent = BaseAgent(client=client, max_retries=3)
            result = await agent.send_message("Hello")

        assert result.content == "ok"
        assert client.messages.create.call_count == 3

    async def test_raises_after_max_retries_exhausted(self) -> None:
        """send_message raises RateLimitError after all retries fail."""
        client = MagicMock(spec=anthropic.Anthropic)
        client.messages.create.side_effect = _make_rate_limit_error()

        with patch("resume_builder.agents.base.asyncio.sleep"):
            agent = BaseAgent(client=client, max_retries=2)
            with pytest.raises(anthropic.RateLimitError):
                await agent.send_message("Hello")

        assert client.messages.create.call_count == 2

    async def test_does_not_retry_on_non_rate_limit_error(self) -> None:
        """send_message does not retry on general API errors."""
        client = MagicMock(spec=anthropic.Anthropic)
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 500
        mock_resp.headers = httpx.Headers({})
        mock_resp.request = MagicMock(spec=httpx.Request)
        server_error = anthropic.InternalServerError(
            message="Server error",
            response=mock_resp,
            body={},
        )
        client.messages.create.side_effect = server_error

        agent = BaseAgent(client=client, max_retries=3)
        with pytest.raises(anthropic.InternalServerError):
            await agent.send_message("Hello")

        assert client.messages.create.call_count == 1

    async def test_exponential_backoff_sleep_called(self) -> None:
        """Retry sleep duration doubles on each attempt (exponential backoff)."""
        client = MagicMock(spec=anthropic.Anthropic)
        error = _make_rate_limit_error()
        client.messages.create.side_effect = [error, error, _make_text_response("ok")]

        with patch("resume_builder.agents.base.asyncio.sleep") as mock_sleep:
            agent = BaseAgent(client=client, max_retries=3)
            await agent.send_message("Hello")

        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert len(sleep_calls) == 2
        assert sleep_calls[1] > sleep_calls[0]  # backoff doubles

"""Tests for agent message and state models.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from resume_builder.models.agent import (
    AgentMessage,
    AgentResponse,
    AgentState,
    ToolCall,
    ToolDefinition,
    ToolResult,
    TokenUsage,
)


class TestToolDefinition:
    """Tests for ToolDefinition model."""

    def test_tool_definition_requires_name(self) -> None:
        """ToolDefinition requires a name field."""
        with pytest.raises(ValidationError):
            ToolDefinition(description="desc", input_schema={})  # type: ignore[call-arg]

    def test_tool_definition_requires_description(self) -> None:
        """ToolDefinition requires a description field."""
        with pytest.raises(ValidationError):
            ToolDefinition(name="tool", input_schema={})  # type: ignore[call-arg]

    def test_tool_definition_valid(self) -> None:
        """ToolDefinition constructs with all required fields."""
        tool = ToolDefinition(
            name="parse_csv",
            description="Parse a CSV file",
            input_schema={
                "type": "object",
                "properties": {"csv_content": {"type": "string"}},
                "required": ["csv_content"],
            },
        )
        assert tool.name == "parse_csv"
        assert tool.description == "Parse a CSV file"
        assert "properties" in tool.input_schema

    def test_tool_definition_serializes_to_anthropic_format(self) -> None:
        """ToolDefinition model_dump matches Anthropic tool format."""
        tool = ToolDefinition(
            name="my_tool",
            description="Does something",
            input_schema={"type": "object", "properties": {}},
        )
        data = tool.model_dump()
        assert data["name"] == "my_tool"
        assert data["description"] == "Does something"
        assert "input_schema" in data


class TestToolCall:
    """Tests for ToolCall model."""

    def test_tool_call_valid(self) -> None:
        """ToolCall constructs from Anthropic API format."""
        call = ToolCall(
            id="toolu_01abc",
            name="parse_csv",
            input={"csv_content": "Name,Title\nAlice,Engineer"},
        )
        assert call.id == "toolu_01abc"
        assert call.name == "parse_csv"
        assert call.input["csv_content"].startswith("Name")

    def test_tool_call_requires_id(self) -> None:
        """ToolCall requires an id field."""
        with pytest.raises(ValidationError):
            ToolCall(name="tool", input={})  # type: ignore[call-arg]


class TestToolResult:
    """Tests for ToolResult model."""

    def test_tool_result_defaults_not_error(self) -> None:
        """ToolResult.is_error defaults to False."""
        result = ToolResult(tool_use_id="toolu_01", content="success")
        assert result.is_error is False

    def test_tool_result_can_be_error(self) -> None:
        """ToolResult.is_error can be set to True for failures."""
        result = ToolResult(tool_use_id="toolu_01", content="failed", is_error=True)
        assert result.is_error is True

    def test_tool_result_content_can_be_string(self) -> None:
        """ToolResult.content accepts a plain string."""
        result = ToolResult(tool_use_id="toolu_01", content="output")
        assert result.content == "output"

    def test_tool_result_content_can_be_list(self) -> None:
        """ToolResult.content accepts a list of dicts (structured output)."""
        result = ToolResult(
            tool_use_id="toolu_01",
            content=[{"type": "text", "text": "output"}],
        )
        assert isinstance(result.content, list)


class TestAgentMessage:
    """Tests for AgentMessage model."""

    def test_agent_message_user_role(self) -> None:
        """AgentMessage constructs with user role."""
        msg = AgentMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_agent_message_assistant_role(self) -> None:
        """AgentMessage constructs with assistant role."""
        msg = AgentMessage(role="assistant", content="Response")
        assert msg.role == "assistant"

    def test_agent_message_content_can_be_list(self) -> None:
        """AgentMessage.content can be a list of content blocks."""
        msg = AgentMessage(
            role="user",
            content=[{"type": "tool_result", "tool_use_id": "x", "content": "ok"}],
        )
        assert isinstance(msg.content, list)


class TestAgentResponse:
    """Tests for AgentResponse model."""

    def test_agent_response_defaults(self) -> None:
        """AgentResponse has sensible defaults for optional fields."""
        resp = AgentResponse(content="Hello")
        assert resp.content == "Hello"
        assert resp.tool_calls == []
        assert resp.stop_reason == "end_turn"

    def test_agent_response_with_tool_calls(self) -> None:
        """AgentResponse can carry tool call records."""
        call = ToolCall(id="toolu_01", name="my_tool", input={})
        resp = AgentResponse(content="", tool_calls=[call], stop_reason="tool_use")
        assert len(resp.tool_calls) == 1
        assert resp.stop_reason == "tool_use"


class TestTokenUsage:
    """Tests for TokenUsage model."""

    def test_token_usage_defaults_zero(self) -> None:
        """TokenUsage initialises all counters to zero."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

    def test_total_tokens_computed(self) -> None:
        """total_tokens is the sum of input and output tokens."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total_tokens == 150

    def test_add_accumulates_tokens(self) -> None:
        """add() merges another TokenUsage into this one."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        usage.add(TokenUsage(input_tokens=200, output_tokens=75))
        assert usage.input_tokens == 300
        assert usage.output_tokens == 125

    def test_estimated_cost_positive(self) -> None:
        """estimated_cost returns a positive float for non-zero usage."""
        usage = TokenUsage(input_tokens=1_000_000, output_tokens=1_000_000)
        assert usage.estimated_cost > 0.0

    def test_zero_usage_zero_cost(self) -> None:
        """estimated_cost is 0.0 when no tokens have been used."""
        assert TokenUsage().estimated_cost == 0.0


class TestAgentState:
    """Tests for AgentState model."""

    def test_agent_state_defaults(self) -> None:
        """AgentState initialises with idle step and empty history."""
        state = AgentState()
        assert state.step == "idle"
        assert state.history == []
        assert state.resume is None

    def test_agent_state_step_transitions(self) -> None:
        """AgentState step can be updated to reflect workflow progress."""
        state = AgentState()
        state.step = "parsing"
        assert state.step == "parsing"

"""Pydantic models for agent messages, tool calls, and workflow state.

These models mirror Anthropic's API message format so that agent code
can pass them directly to the SDK without transformation.

CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, computed_field

from resume_builder.models.resume import Resume


class ToolDefinition(BaseModel):
    """Schema definition for a tool that an agent can invoke.

    Maps directly to the Anthropic API tool format.

    Args:
        name: Unique tool identifier used in tool_use blocks.
        description: Human-readable description for the model.
        input_schema: JSON Schema object describing the tool's parameters.
    """

    name: str
    description: str
    input_schema: dict[str, Any]


class ToolCall(BaseModel):
    """A tool invocation request returned by the model.

    Parsed from a ``tool_use`` content block in an Anthropic API response.

    Args:
        id: Unique identifier for this tool call (used in ToolResult).
        name: Name of the tool to invoke.
        input: Key-value arguments for the tool.
    """

    id: str
    name: str
    input: dict[str, Any]


class ToolResult(BaseModel):
    """The result of executing a tool call.

    Sent back to the model in a ``tool_result`` content block.

    Args:
        tool_use_id: Must match the ``id`` from the corresponding ToolCall.
        content: Tool output — either a plain string or structured content blocks.
        is_error: Set to True when the tool execution failed.
    """

    tool_use_id: str
    content: str | list[dict[str, Any]]
    is_error: bool = False


class AgentMessage(BaseModel):
    """A single message in an agent conversation.

    Args:
        role: Speaker — either ``"user"`` or ``"assistant"``.
        content: Message body — plain text or a list of content blocks.
    """

    role: str
    content: str | list[dict[str, Any]]


class TokenUsage(BaseModel):
    """Tracks Anthropic API token consumption across one or more calls.

    Args:
        input_tokens: Cumulative input (prompt) tokens consumed.
        output_tokens: Cumulative output (completion) tokens consumed.
    """

    input_tokens: int = 0
    output_tokens: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_tokens(self) -> int:
        """Sum of input and output tokens."""
        return self.input_tokens + self.output_tokens

    @computed_field  # type: ignore[prop-decorator]
    @property
    def estimated_cost(self) -> float:
        """Estimated USD cost based on claude-sonnet-4-6 pricing.

        Rates: $3.00 / 1M input tokens, $15.00 / 1M output tokens.
        """
        return (self.input_tokens * 3.0 + self.output_tokens * 15.0) / 1_000_000

    def add(self, other: TokenUsage) -> None:
        """Accumulate token counts from another TokenUsage instance.

        Args:
            other: TokenUsage to merge into this one.
        """
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens


class AgentResponse(BaseModel):
    """The structured result of a single agent send_message call.

    Args:
        content: Text response from the model (empty when stop_reason is tool_use).
        tool_calls: Any tool invocations requested by the model.
        stop_reason: API stop reason — ``"end_turn"`` or ``"tool_use"``.
        usage: Token consumption for this response.
    """

    content: str
    tool_calls: list[ToolCall] = []
    stop_reason: str = "end_turn"
    usage: TokenUsage = TokenUsage()


class AgentState(BaseModel):
    """Shared workflow state passed between agents in the orchestration pipeline.

    Args:
        step: Current pipeline step name (e.g. ``"parsing"``, ``"matching"``).
        history: Conversation history as AgentMessage objects.
        resume: Parsed resume object, populated after the parsing step.
    """

    step: str = "idle"
    history: list[AgentMessage] = []
    resume: Resume | None = None

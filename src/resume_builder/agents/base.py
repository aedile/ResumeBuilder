"""Base agent class providing Claude API integration for all specialist agents.

All agents in the resume builder extend BaseAgent, which handles:
- Anthropic client management and message dispatch
- Tool registration and automatic tool-call execution
- Retry logic with exponential backoff for rate-limit errors
- Token usage accumulation across all API calls

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import anthropic

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable

from resume_builder.models.agent import AgentResponse, TokenUsage, ToolDefinition


class BaseAgent:
    """Shared foundation for all Resume Builder agents.

    Subclasses register domain-specific tools on initialisation and implement
    higher-level methods (e.g. ``parse``, ``analyze``) that delegate to
    ``send_message``.

    Args:
        client: Anthropic client instance. When ``None``, a default client is
            created using the ``ANTHROPIC_API_KEY`` environment variable.
        model: Claude model identifier. Defaults to ``claude-sonnet-4-6``.
        max_tokens: Maximum tokens in a single completion. Defaults to 4096.
        timeout: Per-request timeout in seconds. Defaults to 30.0.
        max_retries: Maximum retry attempts on rate-limit errors. Defaults to 3.
    """

    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.client: anthropic.Anthropic = client or anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self._tools: list[ToolDefinition] = []
        self._tool_handlers: dict[str, Callable[..., Any]] = {}
        self.message_history: list[dict[str, Any]] = []
        self.token_usage: TokenUsage = TokenUsage()
        self.system_prompt: str | None = None

    def register_tool(self, tool_def: ToolDefinition, handler: Callable[..., Any]) -> None:
        """Register a tool that the model may invoke during a conversation.

        Args:
            tool_def: Tool schema forwarded to the Anthropic API.
            handler: Callable invoked when the model requests this tool.
                     Receives the tool's ``input`` dict as keyword arguments.
        """
        self._tools.append(tool_def)
        self._tool_handlers[tool_def.name] = handler

    async def send_message(self, content: str) -> AgentResponse:
        """Send a user message and return the model's response.

        Handles the complete request-response cycle including:
        - Appending the message to history
        - Executing any tool calls requested by the model
        - Accumulating token usage
        - Retrying on rate-limit errors with exponential backoff

        Args:
            content: User message text.

        Returns:
            AgentResponse with the model's final text response.

        Raises:
            anthropic.RateLimitError: After ``max_retries`` attempts are exhausted.
            anthropic.APIError: Immediately for non-retryable API errors.
        """
        self.message_history.append({"role": "user", "content": content})
        return await self._send_with_retry()

    async def _send_with_retry(self) -> AgentResponse:
        """Dispatch the current message history with exponential-backoff retry.

        Only retries on ``RateLimitError`` (HTTP 429). All other API errors
        propagate immediately.

        Returns:
            AgentResponse from the first successful API call.

        Raises:
            anthropic.RateLimitError: When all retry attempts are exhausted.
        """
        last_exc: anthropic.RateLimitError | None = None
        for attempt in range(self.max_retries):
            try:
                return await self._do_send()
            except anthropic.RateLimitError as exc:
                last_exc = exc
                await asyncio.sleep(2.0**attempt)
        raise last_exc  # type: ignore[misc]

    async def _do_send(self) -> AgentResponse:
        """Perform a single API call and process the response.

        Builds the tool list from registered tools, calls the Anthropic API,
        updates token usage, and delegates to ``_handle_tool_calls`` when the
        model requests tool use.

        Returns:
            AgentResponse containing the model's text output.
        """
        tools_payload: list[dict[str, Any]] = [t.model_dump() for t in self._tools]

        response = self.client.messages.create(  # type: ignore[call-overload]
            # Runtime-valid: message_history holds MessageParam-shaped dicts and
            # tools_payload holds ToolParam-shaped dicts. Mypy cannot resolve the
            # conditional **kwargs spread against the SDK's overloaded signatures.
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self.message_history,
            **({"tools": tools_payload} if tools_payload else {}),
            **({"system": self.system_prompt} if self.system_prompt is not None else {}),
        )

        self.token_usage.add(
            TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )
        )

        self.message_history.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            return await self._handle_tool_calls(response)

        text = next(
            (block.text for block in response.content if hasattr(block, "text")),
            "",
        )
        return AgentResponse(content=text, stop_reason=response.stop_reason)

    def get_usage_report(self) -> dict[str, Any]:
        """Return a summary of token usage for this agent.

        Returns:
            Dict with ``input_tokens``, ``output_tokens``, ``total_tokens``,
            and ``estimated_cost`` for all API calls made by this agent.
        """
        return self.token_usage.model_dump()

    async def _handle_tool_calls(self, response: Any) -> AgentResponse:
        """Execute each tool requested by the model and send results back.

        Iterates over ``tool_use`` blocks in the response, calls the registered
        handler for each, and sends all results back in a single user message
        before continuing the conversation.

        Args:
            response: Raw Anthropic API response with ``stop_reason == "tool_use"``.

        Returns:
            AgentResponse from the follow-up API call after tool execution.
        """
        tool_results: list[dict[str, Any]] = []

        for block in response.content:
            if block.type == "tool_use":
                handler = self._tool_handlers.get(block.name)
                if handler is None:
                    logger.warning("Unknown tool requested by model: %s", block.name)
                result = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )

        self.message_history.append({"role": "user", "content": tool_results})
        return await self._do_send()

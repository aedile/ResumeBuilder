"""Tests for token tracking — BaseAgent.get_usage_report() and TokenUsage model.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tests use mocked Anthropic clients — no real API calls ever made.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import anthropic
import pytest

from resume_builder.agents.base import BaseAgent
from resume_builder.models.agent import TokenUsage

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_text_response(input_tokens: int = 100, output_tokens: int = 50) -> MagicMock:
    """Build a mock Anthropic response with configurable token counts."""
    block = MagicMock()
    block.type = "text"
    block.text = "response"

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = input_tokens
    response.usage.output_tokens = output_tokens
    return response


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked Anthropic client."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response(100, 50)
    return client


# ---------------------------------------------------------------------------
# TokenUsage model tests
# ---------------------------------------------------------------------------


class TestTokenUsageModel:
    """Tests for the TokenUsage Pydantic model."""

    def test_token_usage_defaults_to_zero(self) -> None:
        """TokenUsage initialises with zero counts."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

    def test_total_tokens_computed(self) -> None:
        """total_tokens is the sum of input and output tokens."""
        usage = TokenUsage(input_tokens=300, output_tokens=150)
        assert usage.total_tokens == 450

    def test_estimated_cost_calculation(self) -> None:
        """estimated_cost applies correct per-token rates."""
        # $3/1M input, $15/1M output
        usage = TokenUsage(input_tokens=1_000_000, output_tokens=1_000_000)
        assert usage.estimated_cost == pytest.approx(18.0)

    def test_estimated_cost_zero_for_no_tokens(self) -> None:
        """estimated_cost is 0.0 when no tokens consumed."""
        usage = TokenUsage()
        assert usage.estimated_cost == 0.0

    def test_add_accumulates_tokens(self) -> None:
        """add() merges another TokenUsage into this one."""
        base = TokenUsage(input_tokens=100, output_tokens=50)
        extra = TokenUsage(input_tokens=200, output_tokens=80)
        base.add(extra)
        assert base.input_tokens == 300
        assert base.output_tokens == 130

    def test_add_multiple_times(self) -> None:
        """add() is cumulative across multiple calls."""
        total = TokenUsage()
        for _ in range(3):
            total.add(TokenUsage(input_tokens=10, output_tokens=5))
        assert total.total_tokens == 45


# ---------------------------------------------------------------------------
# BaseAgent.get_usage_report() tests
# ---------------------------------------------------------------------------


class TestBaseAgentGetUsageReport:
    """Tests for BaseAgent.get_usage_report()."""

    def test_get_usage_report_returns_dict(self, mock_client: MagicMock) -> None:
        """get_usage_report() returns a dict."""
        agent = BaseAgent(client=mock_client)
        report = agent.get_usage_report()
        assert isinstance(report, dict)

    def test_get_usage_report_includes_required_keys(self, mock_client: MagicMock) -> None:
        """get_usage_report() contains input_tokens, output_tokens, total_tokens, estimated_cost."""
        agent = BaseAgent(client=mock_client)
        report = agent.get_usage_report()
        assert "input_tokens" in report
        assert "output_tokens" in report
        assert "total_tokens" in report
        assert "estimated_cost" in report

    def test_get_usage_report_initial_zeros(self, mock_client: MagicMock) -> None:
        """get_usage_report() shows zeros before any API calls."""
        agent = BaseAgent(client=mock_client)
        report = agent.get_usage_report()
        assert report["input_tokens"] == 0
        assert report["output_tokens"] == 0
        assert report["total_tokens"] == 0

    async def test_get_usage_report_after_api_call(self, mock_client: MagicMock) -> None:
        """get_usage_report() reflects token counts from a real API call."""
        mock_client.messages.create.return_value = _make_text_response(200, 75)
        agent = BaseAgent(client=mock_client)
        await agent.send_message("Hello")
        report = agent.get_usage_report()
        assert report["input_tokens"] == 200
        assert report["output_tokens"] == 75
        assert report["total_tokens"] == 275

    async def test_get_usage_report_accumulates_across_calls(self, mock_client: MagicMock) -> None:
        """get_usage_report() accumulates tokens across multiple send_message calls."""
        mock_client.messages.create.return_value = _make_text_response(100, 50)
        agent = BaseAgent(client=mock_client)
        await agent.send_message("First message")
        await agent.send_message("Second message")
        report = agent.get_usage_report()
        assert report["total_tokens"] == 300  # 150 x 2

    def test_get_usage_report_total_equals_input_plus_output(self, mock_client: MagicMock) -> None:
        """get_usage_report() total_tokens == input_tokens + output_tokens."""
        agent = BaseAgent(client=mock_client)
        agent.token_usage = TokenUsage(input_tokens=123, output_tokens=456)
        report = agent.get_usage_report()
        assert report["total_tokens"] == report["input_tokens"] + report["output_tokens"]

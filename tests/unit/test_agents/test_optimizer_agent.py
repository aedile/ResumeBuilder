"""Tests for OptimizerAgent.

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
from resume_builder.agents.optimizer_agent import OptimizerAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.match import JobDescription, MatchReport
from resume_builder.models.optimizer import OptimizedResume
from resume_builder.models.resume import Profile, Resume

_MINIMAL_OPTIMIZED_RESUME_JSON = json.dumps(
    {
        "summary": "Experienced Software Engineer with expertise in Python and Docker.",
        "optimized_bullets": {
            "Senior Engineer at Acme": [
                "Led development of Python microservices reducing latency by 40%.",
                "Architected Docker-based deployment pipeline cutting release time by 50%.",
            ]
        },
        "changes": [
            "Rewrote summary to include job-specific keywords",
            "Added quantifiable metrics to bullet points",
        ],
    }
)


def _make_text_response(text: str = _MINIMAL_OPTIMIZED_RESUME_JSON) -> MagicMock:
    """Build a mock Anthropic response with a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = 150
    response.usage.output_tokens = 80
    return response


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked Anthropic client returning a minimal OptimizedResume JSON."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


@pytest.fixture
def sample_resume() -> Resume:
    """Minimal Resume fixture for optimizer tests."""
    return Resume(
        profile=Profile(
            first_name="Alex",
            last_name="Chen",
            headline="Software Engineer",
        )
    )


@pytest.fixture
def sample_job() -> JobDescription:
    """Minimal JobDescription fixture for optimizer tests."""
    return JobDescription(
        title="Senior Software Engineer",
        description="We need Python and Docker expertise. 5+ years required.",
    )


@pytest.fixture
def sample_match() -> MatchReport:
    """Minimal MatchReport fixture for optimizer tests."""
    return MatchReport(
        overall_score=75,
        gaps=["kubernetes"],
        recommendations=["Add Kubernetes experience"],
    )


class TestOptimizerAgentInit:
    """OptimizerAgent initialization and tool registration tests."""

    def test_optimizer_agent_extends_base_agent(self, mock_client: MagicMock) -> None:
        """OptimizerAgent is a subclass of BaseAgent."""
        agent = OptimizerAgent(client=mock_client)
        assert isinstance(agent, BaseAgent)

    def test_optimizer_agent_registers_four_tools(self, mock_client: MagicMock) -> None:
        """OptimizerAgent registers exactly four optimization tools."""
        agent = OptimizerAgent(client=mock_client)
        assert len(agent._tools) == 4

    def test_optimizer_agent_has_rewrite_bullet_tool(self, mock_client: MagicMock) -> None:
        """OptimizerAgent registers the rewrite_bullet tool."""
        agent = OptimizerAgent(client=mock_client)
        assert "rewrite_bullet" in [t.name for t in agent._tools]

    def test_optimizer_agent_has_generate_summary_tool(self, mock_client: MagicMock) -> None:
        """OptimizerAgent registers the generate_summary tool."""
        agent = OptimizerAgent(client=mock_client)
        assert "generate_summary" in [t.name for t in agent._tools]

    def test_optimizer_agent_has_suggest_edits_tool(self, mock_client: MagicMock) -> None:
        """OptimizerAgent registers the suggest_edits tool."""
        agent = OptimizerAgent(client=mock_client)
        assert "suggest_edits" in [t.name for t in agent._tools]

    def test_optimizer_agent_has_verify_facts_tool(self, mock_client: MagicMock) -> None:
        """OptimizerAgent registers the verify_facts tool."""
        agent = OptimizerAgent(client=mock_client)
        assert "verify_facts" in [t.name for t in agent._tools]

    def test_optimizer_agent_has_system_prompt(self, mock_client: MagicMock) -> None:
        """OptimizerAgent defines a non-empty SYSTEM_PROMPT class attribute."""
        assert hasattr(OptimizerAgent, "SYSTEM_PROMPT")
        assert isinstance(OptimizerAgent.SYSTEM_PROMPT, str)
        assert len(OptimizerAgent.SYSTEM_PROMPT) > 50

    def test_optimizer_agent_all_handlers_callable(self, mock_client: MagicMock) -> None:
        """OptimizerAgent tool names all map to callable handlers."""
        agent = OptimizerAgent(client=mock_client)
        for name in ("rewrite_bullet", "generate_summary", "suggest_edits", "verify_facts"):
            assert callable(agent._tool_handlers[name])


class TestOptimizerAgentOptimize:
    """OptimizerAgent.optimize() method tests."""

    async def test_optimize_returns_optimized_resume(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() returns an OptimizedResume instance on success."""
        agent = OptimizerAgent(client=mock_client)
        result = await agent.optimize(sample_resume, sample_job, sample_match)
        assert isinstance(result, OptimizedResume)

    async def test_optimize_populates_summary(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() returns OptimizedResume with summary from API response."""
        agent = OptimizerAgent(client=mock_client)
        result = await agent.optimize(sample_resume, sample_job, sample_match)
        assert "Python" in result.summary or "Engineer" in result.summary

    async def test_optimize_populates_changes(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() returns OptimizedResume with changes list from API response."""
        agent = OptimizerAgent(client=mock_client)
        result = await agent.optimize(sample_resume, sample_job, sample_match)
        assert len(result.changes) > 0

    async def test_optimize_sends_resume_and_job_in_message(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() includes resume and job data in the API message."""
        agent = OptimizerAgent(client=mock_client)
        await agent.optimize(sample_resume, sample_job, sample_match)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert sample_job.title in user_message["content"]

    async def test_optimize_invalid_json_raises_parse_error(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() raises ParseError when API returns non-JSON text."""
        mock_client.messages.create.return_value = _make_text_response("not valid json")
        agent = OptimizerAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.optimize(sample_resume, sample_job, sample_match)

    async def test_optimize_invalid_schema_raises_parse_error(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() raises ParseError when JSON doesn't match OptimizedResume schema."""
        mock_client.messages.create.return_value = _make_text_response('{"bad": "schema"}')
        agent = OptimizerAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.optimize(sample_resume, sample_job, sample_match)

    async def test_optimize_accumulates_token_usage(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() accumulates token usage from the API call."""
        agent = OptimizerAgent(client=mock_client)
        await agent.optimize(sample_resume, sample_job, sample_match)
        assert agent.token_usage.total_tokens > 0

    async def test_optimize_passes_system_prompt(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() includes the system prompt in the API call."""
        agent = OptimizerAgent(client=mock_client)
        await agent.optimize(sample_resume, sample_job, sample_match)
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs.get("system") == OptimizerAgent.SYSTEM_PROMPT

    async def test_optimize_sends_match_gaps_in_message(
        self,
        mock_client: MagicMock,
        sample_resume: Resume,
        sample_job: JobDescription,
        sample_match: MatchReport,
    ) -> None:
        """optimize() includes match gaps in the API message for targeted improvement."""
        agent = OptimizerAgent(client=mock_client)
        await agent.optimize(sample_resume, sample_job, sample_match)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "kubernetes" in user_message["content"].lower()


class TestOptimizedResumeModel:
    """Tests for the OptimizedResume model."""

    def test_optimized_resume_defaults(self) -> None:
        """OptimizedResume can be created with all defaults."""
        result = OptimizedResume()
        assert result.summary is None
        assert result.optimized_bullets == {}
        assert result.changes == []

    def test_optimized_resume_full_construction(self) -> None:
        """OptimizedResume accepts all fields."""
        result = OptimizedResume(
            summary="Experienced engineer...",
            optimized_bullets={"Role A": ["Led team...", "Built system..."]},
            changes=["Added metrics", "Rewrote summary"],
        )
        assert result.summary == "Experienced engineer..."
        assert len(result.optimized_bullets["Role A"]) == 2
        assert len(result.changes) == 2

    def test_optimized_resume_serializes_to_json(self) -> None:
        """OptimizedResume serializes to JSON via model_dump_json."""
        result = OptimizedResume(
            summary="Test summary",
            changes=["change 1"],
        )
        data = json.loads(result.model_dump_json())
        assert data["summary"] == "Test summary"
        assert data["changes"] == ["change 1"]

    def test_optimized_resume_invalid_schema_rejected(self) -> None:
        """OptimizedResume rejects unknown fields (extra='forbid')."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizedResume(**{"bad_field": "value"})  # type: ignore[arg-type]

"""Tests for MatcherAgent.

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
from resume_builder.agents.matcher_agent import MatcherAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.match import JobDescription, MatchReport
from resume_builder.models.resume import Profile, Resume

_MINIMAL_MATCH_REPORT_JSON = json.dumps(
    {
        "overall_score": 85,
        "section_scores": {"skills": 90, "experience": 80},
        "gaps": ["kubernetes"],
        "recommendations": ["Add Kubernetes experience"],
        "ranked_positions": ["Senior Engineer at Acme"],
    }
)


def _make_text_response(text: str = _MINIMAL_MATCH_REPORT_JSON) -> MagicMock:
    """Build a mock Anthropic response with a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text

    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = 120
    response.usage.output_tokens = 60
    return response


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked Anthropic client returning a minimal MatchReport JSON."""
    client = MagicMock(spec=anthropic.Anthropic)
    client.messages.create.return_value = _make_text_response()
    return client


@pytest.fixture
def sample_resume() -> Resume:
    """Minimal Resume fixture for matcher tests."""
    return Resume(
        profile=Profile(
            first_name="Alex",
            last_name="Chen",
            headline="Software Engineer",
        )
    )


@pytest.fixture
def sample_job() -> JobDescription:
    """Minimal JobDescription fixture for matcher tests."""
    return JobDescription(
        title="Senior Software Engineer",
        description="We need Python and Docker expertise. 5+ years required.",
    )


class TestMatcherAgentInit:
    """MatcherAgent initialization and tool registration tests."""

    def test_matcher_agent_extends_base_agent(self, mock_client: MagicMock) -> None:
        """MatcherAgent is a subclass of BaseAgent."""
        agent = MatcherAgent(client=mock_client)
        assert isinstance(agent, BaseAgent)

    def test_matcher_agent_registers_four_tools(self, mock_client: MagicMock) -> None:
        """MatcherAgent registers exactly four matching tools."""
        agent = MatcherAgent(client=mock_client)
        assert len(agent._tools) == 4  # noqa: PLR2004

    def test_matcher_agent_has_extract_requirements_tool(self, mock_client: MagicMock) -> None:
        """MatcherAgent registers the extract_requirements tool."""
        agent = MatcherAgent(client=mock_client)
        assert "extract_requirements" in [t.name for t in agent._tools]

    def test_matcher_agent_has_score_match_tool(self, mock_client: MagicMock) -> None:
        """MatcherAgent registers the score_match tool."""
        agent = MatcherAgent(client=mock_client)
        assert "score_match" in [t.name for t in agent._tools]

    def test_matcher_agent_has_identify_gaps_tool(self, mock_client: MagicMock) -> None:
        """MatcherAgent registers the identify_gaps tool."""
        agent = MatcherAgent(client=mock_client)
        assert "identify_gaps" in [t.name for t in agent._tools]

    def test_matcher_agent_has_rank_experience_tool(self, mock_client: MagicMock) -> None:
        """MatcherAgent registers the rank_experience tool."""
        agent = MatcherAgent(client=mock_client)
        assert "rank_experience" in [t.name for t in agent._tools]

    def test_matcher_agent_has_system_prompt(self, mock_client: MagicMock) -> None:
        """MatcherAgent defines a non-empty SYSTEM_PROMPT class attribute."""
        assert hasattr(MatcherAgent, "SYSTEM_PROMPT")
        assert isinstance(MatcherAgent.SYSTEM_PROMPT, str)
        assert len(MatcherAgent.SYSTEM_PROMPT) > 50  # noqa: PLR2004

    def test_matcher_agent_all_handlers_callable(self, mock_client: MagicMock) -> None:
        """MatcherAgent tool names all map to callable handlers."""
        agent = MatcherAgent(client=mock_client)
        for name in ("extract_requirements", "score_match", "identify_gaps", "rank_experience"):
            assert callable(agent._tool_handlers[name])


class TestMatcherAgentAnalyze:
    """MatcherAgent.analyze() method tests."""

    async def test_analyze_returns_match_report(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() returns a MatchReport instance on success."""
        agent = MatcherAgent(client=mock_client)
        result = await agent.analyze(sample_resume, sample_job)
        assert isinstance(result, MatchReport)

    async def test_analyze_populates_overall_score(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() returns a MatchReport with overall_score from API response."""
        agent = MatcherAgent(client=mock_client)
        result = await agent.analyze(sample_resume, sample_job)
        assert result.overall_score == 85  # noqa: PLR2004

    async def test_analyze_populates_gaps(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() returns a MatchReport with gaps from API response."""
        agent = MatcherAgent(client=mock_client)
        result = await agent.analyze(sample_resume, sample_job)
        assert "kubernetes" in result.gaps

    async def test_analyze_sends_resume_and_job_in_message(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() includes both resume and job data in the API message."""
        agent = MatcherAgent(client=mock_client)
        await agent.analyze(sample_resume, sample_job)
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert sample_job.title in user_message["content"]

    async def test_analyze_invalid_json_raises_parse_error(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() raises ParseError when API returns non-JSON text."""
        mock_client.messages.create.return_value = _make_text_response("not valid json")
        agent = MatcherAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.analyze(sample_resume, sample_job)

    async def test_analyze_invalid_schema_raises_parse_error(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() raises ParseError when JSON doesn't match MatchReport schema."""
        mock_client.messages.create.return_value = _make_text_response('{"bad": "schema"}')
        agent = MatcherAgent(client=mock_client)
        with pytest.raises(ParseError):
            await agent.analyze(sample_resume, sample_job)

    async def test_analyze_accumulates_token_usage(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() accumulates token usage from the API call."""
        agent = MatcherAgent(client=mock_client)
        await agent.analyze(sample_resume, sample_job)
        assert agent.token_usage.total_tokens > 0

    async def test_analyze_passes_system_prompt(
        self, mock_client: MagicMock, sample_resume: Resume, sample_job: JobDescription
    ) -> None:
        """analyze() includes the system prompt in the API call."""
        agent = MatcherAgent(client=mock_client)
        await agent.analyze(sample_resume, sample_job)
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs.get("system") == MatcherAgent.SYSTEM_PROMPT


class TestJobDescriptionModel:
    """Tests for the JobDescription model."""

    def test_job_description_requires_title(self) -> None:
        """JobDescription requires a title field."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            JobDescription(description="Text only")  # type: ignore[call-arg]

    def test_job_description_requires_description(self) -> None:
        """JobDescription requires a description field."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            JobDescription(title="Engineer")  # type: ignore[call-arg]

    def test_job_description_optional_company(self) -> None:
        """JobDescription company defaults to None."""
        job = JobDescription(title="Engineer", description="Python dev needed")
        assert job.company is None

    def test_job_description_optional_skills(self) -> None:
        """JobDescription required_skills defaults to empty list."""
        job = JobDescription(title="Engineer", description="Python dev needed")
        assert job.required_skills == []

    def test_job_description_full_construction(self) -> None:
        """JobDescription accepts all optional fields."""
        job = JobDescription(
            title="Senior Engineer",
            description="Python and AWS",
            company="Acme Corp",
            required_skills=["python", "aws"],
            years_experience=5,
        )
        assert job.company == "Acme Corp"
        assert job.years_experience == 5


class TestMatchReportModel:
    """Tests for the MatchReport model."""

    def test_match_report_defaults(self) -> None:
        """MatchReport can be created with all defaults."""
        report = MatchReport()
        assert report.overall_score == 0
        assert report.gaps == []
        assert report.recommendations == []

    def test_match_report_score_range(self) -> None:
        """MatchReport overall_score is set correctly."""
        report = MatchReport(overall_score=75)
        assert report.overall_score == 75  # noqa: PLR2004

    def test_match_report_full_construction(self) -> None:
        """MatchReport accepts all fields."""
        report = MatchReport(
            overall_score=85,
            section_scores={"skills": 90, "experience": 80},
            gaps=["kubernetes"],
            recommendations=["Learn Kubernetes"],
            ranked_positions=["Senior Engineer at Acme"],
        )
        assert report.overall_score == 85  # noqa: PLR2004
        assert "kubernetes" in report.gaps

    def test_match_report_serializes_to_json(self) -> None:
        """MatchReport serializes to JSON via model_dump_json."""
        report = MatchReport(overall_score=70, gaps=["docker"])
        data = json.loads(report.model_dump_json())
        assert data["overall_score"] == 70  # noqa: PLR2004


class TestBaseAgentSystemPrompt:
    """Tests for BaseAgent system_prompt attribute (added in this task)."""

    def test_base_agent_system_prompt_default_none(self, mock_client: MagicMock) -> None:
        """BaseAgent.system_prompt defaults to None."""
        agent = BaseAgent(client=mock_client)
        assert agent.system_prompt is None

    async def test_base_agent_no_system_when_none(self, mock_client: MagicMock) -> None:
        """BaseAgent does not pass system to API when system_prompt is None."""
        agent = BaseAgent(client=mock_client)
        await agent.send_message("hello")
        call_args = mock_client.messages.create.call_args
        assert "system" not in call_args.kwargs

    async def test_base_agent_sends_system_when_set(self, mock_client: MagicMock) -> None:
        """BaseAgent passes system to API when system_prompt is set."""
        agent = BaseAgent(client=mock_client)
        agent.system_prompt = "You are a helpful assistant."

        # Patch _make_text_response-style mock
        block = MagicMock()
        block.type = "text"
        block.text = "ok"
        resp = MagicMock()
        resp.content = [block]
        resp.stop_reason = "end_turn"
        resp.usage.input_tokens = 10
        resp.usage.output_tokens = 5
        mock_client.messages.create.return_value = resp

        await agent.send_message("hello")
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs.get("system") == "You are a helpful assistant."

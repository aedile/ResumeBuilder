"""Tests for OrchestratorAgent.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tests use mocked sub-agents — no real API calls ever made.
"""

from __future__ import annotations

import json
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from resume_builder.agents.orchestrator import OrchestratorAgent
from resume_builder.exceptions import ParseError
from resume_builder.models.agent import TokenUsage
from resume_builder.models.match import JobDescription, MatchReport
from resume_builder.models.optimizer import OptimizedResume
from resume_builder.models.orchestrator import FinalResult
from resume_builder.models.resume import Profile, Resume

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_resume() -> Resume:
    return Resume(profile=Profile(first_name="Alex", last_name="Chen", headline="Engineer"))


def _make_match() -> MatchReport:
    return MatchReport(
        overall_score=80,
        gaps=["kubernetes"],
        recommendations=["Add Kubernetes"],
    )


def _make_optimized() -> OptimizedResume:
    return OptimizedResume(
        summary="Experienced engineer.",
        changes=["Rewrote summary"],
    )


@pytest.fixture
def mock_parser() -> MagicMock:
    """Mocked ParserAgent."""
    agent = MagicMock()
    agent.parse = AsyncMock(return_value=_make_resume())
    agent.token_usage = TokenUsage(input_tokens=100, output_tokens=50)
    return agent


@pytest.fixture
def mock_matcher() -> MagicMock:
    """Mocked MatcherAgent."""
    agent = MagicMock()
    agent.analyze = AsyncMock(return_value=_make_match())
    agent.token_usage = TokenUsage(input_tokens=200, output_tokens=80)
    return agent


@pytest.fixture
def mock_optimizer() -> MagicMock:
    """Mocked OptimizerAgent."""
    agent = MagicMock()
    agent.optimize = AsyncMock(return_value=_make_optimized())
    agent.token_usage = TokenUsage(input_tokens=300, output_tokens=120)
    return agent


@pytest.fixture
def sample_job() -> JobDescription:
    return JobDescription(
        title="Senior Engineer",
        description="We need Python and Docker.",
    )


@pytest.fixture
def linkedin_data() -> dict[str, str]:
    return {"profile": "First Name,Last Name\nAlex,Chen"}


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestOrchestratorAgentInit:
    """OrchestratorAgent initialisation tests."""

    def test_orchestrator_accepts_pre_built_agents(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
    ) -> None:
        """OrchestratorAgent stores pre-built agent instances."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        assert orch.parser is mock_parser
        assert orch.matcher is mock_matcher
        assert orch.optimizer is mock_optimizer

    def test_orchestrator_initialises_state(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
    ) -> None:
        """OrchestratorAgent starts in 'idle' state."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        assert orch.state.step == "idle"

    def test_orchestrator_creates_default_agents_from_client(self) -> None:
        """OrchestratorAgent creates sub-agents when none provided."""
        mock_client = MagicMock()
        orch = OrchestratorAgent(client=mock_client)
        assert orch.parser is not None
        assert orch.matcher is not None
        assert orch.optimizer is not None


# ---------------------------------------------------------------------------
# run() happy-path tests
# ---------------------------------------------------------------------------


class TestOrchestratorAgentRun:
    """OrchestratorAgent.run() method tests."""

    async def test_run_returns_final_result(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() returns a FinalResult on the happy path."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result, FinalResult)

    async def test_run_result_contains_optimized_resume(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() result.resume is an OptimizedResume."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result.resume, OptimizedResume)

    async def test_run_result_contains_match_report(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() result.match contains the MatchReport."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result.match, MatchReport)
        assert result.match.overall_score == 80

    async def test_run_passes_linkedin_data_to_parser(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() forwards linkedin_data to parser.parse()."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        await orch.run(linkedin_data, sample_job)
        mock_parser.parse.assert_awaited_once_with(linkedin_data)

    async def test_run_passes_resume_and_job_to_matcher(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() passes parsed resume and job to matcher.analyze()."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        resume = _make_resume()
        mock_parser.parse.return_value = resume
        await orch.run(linkedin_data, sample_job)
        mock_matcher.analyze.assert_awaited_once_with(resume, sample_job)

    async def test_run_passes_resume_job_match_to_optimizer(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() passes resume, job, and match to optimizer.optimize()."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        resume = _make_resume()
        match = _make_match()
        mock_parser.parse.return_value = resume
        mock_matcher.analyze.return_value = match
        await orch.run(linkedin_data, sample_job)
        mock_optimizer.optimize.assert_awaited_once_with(resume, sample_job, match)

    async def test_run_no_errors_on_success(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() result.errors is empty on success."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert result.errors == []


# ---------------------------------------------------------------------------
# Progress callback tests
# ---------------------------------------------------------------------------


class TestOrchestratorProgress:
    """Progress callback tests."""

    async def test_run_calls_progress_for_each_step(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() calls on_progress with 'parsing', 'matching', 'optimizing', 'complete'."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        progress_steps: list[str] = []
        await orch.run(linkedin_data, sample_job, on_progress=progress_steps.append)
        assert progress_steps == ["parsing", "matching", "optimizing", "complete"]

    async def test_run_works_without_progress_callback(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() completes normally when on_progress is None."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job, on_progress=None)
        assert isinstance(result, FinalResult)

    async def test_run_updates_state_step(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() sets state.step to 'complete' after successful run."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        await orch.run(linkedin_data, sample_job)
        assert orch.state.step == "complete"


# ---------------------------------------------------------------------------
# Human-in-the-loop approval tests
# ---------------------------------------------------------------------------


class TestOrchestratorApproval:
    """Human-in-the-loop approval callback tests."""

    async def test_run_approval_approved_continues_to_optimizer(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """When approval_callback returns True, optimizer runs normally."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job, approval_callback=lambda _match: True)
        mock_optimizer.optimize.assert_awaited_once()
        assert result.errors == []

    async def test_run_approval_rejected_skips_optimizer(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """When approval_callback returns False, optimizer is skipped."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job, approval_callback=lambda _match: False)
        mock_optimizer.optimize.assert_not_awaited()
        assert "approval" in result.errors[0].lower()

    async def test_run_approval_rejected_still_returns_match(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """When approval_callback returns False, match is still in result."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job, approval_callback=lambda _match: False)
        assert isinstance(result.match, MatchReport)

    async def test_run_no_approval_callback_skips_check(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() with no approval_callback always proceeds to optimizer."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        await orch.run(linkedin_data, sample_job)
        mock_optimizer.optimize.assert_awaited_once()


# ---------------------------------------------------------------------------
# Failure / partial-result tests
# ---------------------------------------------------------------------------


class TestOrchestratorFailures:
    """Orchestrator failure handling tests."""

    async def test_run_parser_failure_raises_parse_error(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() re-raises ParseError when parser fails."""
        mock_parser.parse.side_effect = ParseError("bad data")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        with pytest.raises(ParseError):
            await orch.run(linkedin_data, sample_job)

    async def test_run_matcher_failure_raises_parse_error(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() re-raises ParseError when matcher fails."""
        mock_matcher.analyze.side_effect = ParseError("bad match")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        with pytest.raises(ParseError):
            await orch.run(linkedin_data, sample_job)

    async def test_run_optimizer_failure_returns_partial_result(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() returns partial FinalResult when optimizer fails."""
        mock_optimizer.optimize.side_effect = ParseError("optimizer error")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result, FinalResult)
        assert len(result.errors) > 0

    async def test_run_optimizer_failure_preserves_match(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() preserves match report even when optimizer fails."""
        mock_optimizer.optimize.side_effect = ParseError("optimizer error")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result.match, MatchReport)

    async def test_run_optimizer_failure_returns_empty_resume(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """run() returns empty OptimizedResume when optimizer fails."""
        mock_optimizer.optimize.side_effect = ParseError("optimizer error")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result.resume, OptimizedResume)
        assert result.resume.summary is None
        assert result.resume.changes == []

    async def test_run_optimizer_failure_logs_error(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """run() logs an ERROR when the optimizer step raises an exception."""
        mock_optimizer.optimize.side_effect = ParseError("optimizer blew up")
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        with caplog.at_level(logging.ERROR, logger="resume_builder.agents.orchestrator"):
            await orch.run(linkedin_data, sample_job)

        assert any(
            "optimizer" in r.message.lower() and r.levelno == logging.ERROR
            for r in caplog.records
        )


# ---------------------------------------------------------------------------
# Token usage / get_usage_report tests
# ---------------------------------------------------------------------------


class TestOrchestratorTokenUsage:
    """Token usage aggregation tests for OrchestratorAgent."""

    async def test_run_result_has_token_usage(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """FinalResult contains aggregated token usage."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert isinstance(result.token_usage, TokenUsage)

    async def test_run_result_aggregates_all_agents_tokens(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
        sample_job: JobDescription,
        linkedin_data: dict[str, str],
    ) -> None:
        """FinalResult.token_usage sums tokens from all three agents."""
        # Parser: 100+50=150, Matcher: 200+80=280, Optimizer: 300+120=420 → total 850
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        result = await orch.run(linkedin_data, sample_job)
        assert result.token_usage.total_tokens == 850

    def test_get_usage_report_structure(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
    ) -> None:
        """get_usage_report() returns dict with per-agent and total keys."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        report = orch.get_usage_report()
        assert "parser" in report
        assert "matcher" in report
        assert "optimizer" in report
        assert "total" in report

    def test_get_usage_report_total_matches_sum(
        self,
        mock_parser: MagicMock,
        mock_matcher: MagicMock,
        mock_optimizer: MagicMock,
    ) -> None:
        """get_usage_report() total_tokens equals sum of all agents."""
        orch = OrchestratorAgent(parser=mock_parser, matcher=mock_matcher, optimizer=mock_optimizer)
        report = orch.get_usage_report()
        per_agent = (
            report["parser"]["total_tokens"]
            + report["matcher"]["total_tokens"]
            + report["optimizer"]["total_tokens"]
        )
        assert report["total"]["total_tokens"] == per_agent


# ---------------------------------------------------------------------------
# FinalResult model tests
# ---------------------------------------------------------------------------


class TestFinalResultModel:
    """Tests for the FinalResult Pydantic model."""

    def test_final_result_defaults(self) -> None:
        """FinalResult has sensible defaults."""
        result = FinalResult(resume=OptimizedResume(), token_usage=TokenUsage())
        assert result.match is None
        assert result.errors == []

    def test_final_result_full_construction(self) -> None:
        """FinalResult accepts all fields."""
        result = FinalResult(
            resume=OptimizedResume(summary="Great engineer"),
            match=MatchReport(overall_score=90),
            token_usage=TokenUsage(input_tokens=100, output_tokens=50),
            errors=["optimizer skipped"],
        )
        assert result.resume.summary == "Great engineer"
        assert result.match is not None
        assert result.match.overall_score == 90
        assert result.token_usage.total_tokens == 150
        assert len(result.errors) == 1

    def test_final_result_serializes_to_json(self) -> None:
        """FinalResult serializes cleanly via model_dump_json."""
        result = FinalResult(
            resume=OptimizedResume(changes=["rewrote summary"]),
            token_usage=TokenUsage(input_tokens=50, output_tokens=25),
        )
        data = json.loads(result.model_dump_json())
        assert data["errors"] == []
        assert data["token_usage"]["input_tokens"] == 50

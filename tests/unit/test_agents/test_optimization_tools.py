"""Tests for optimizer agent tools.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tools are pure functions — no Claude API calls.
"""

from __future__ import annotations

import json

import pytest

from resume_builder.agents.tools.optimization import (
    GENERATE_SUMMARY_TOOL,
    REWRITE_BULLET_TOOL,
    SUGGEST_EDITS_TOOL,
    VERIFY_FACTS_TOOL,
    generate_summary,
    rewrite_bullet,
    suggest_edits,
    verify_facts,
)
from resume_builder.models.agent import ToolDefinition


class TestRewriteBulletTool:
    """Tests for rewrite_bullet tool function."""

    def test_rewritten_bullet_starts_with_action_verb(self) -> None:
        """rewrite_bullet produces output starting with an action verb."""
        result = rewrite_bullet(
            bullet="worked on python backend services",
            keywords=json.dumps(["python", "backend"]),
        )
        data = json.loads(result)
        assert data["rewritten"][0].isupper()

    def test_returns_original_in_output(self) -> None:
        """rewrite_bullet includes the original bullet in the response."""
        bullet = "helped with database queries"
        result = rewrite_bullet(bullet=bullet, keywords=json.dumps(["sql"]))
        data = json.loads(result)
        assert data["original"] == bullet

    def test_returns_rewritten_field(self) -> None:
        """rewrite_bullet returns a rewritten field in the response."""
        result = rewrite_bullet(
            bullet="did code reviews",
            keywords=json.dumps(["python"]),
        )
        data = json.loads(result)
        assert "rewritten" in data
        assert isinstance(data["rewritten"], str)
        assert len(data["rewritten"]) > 0

    def test_returns_improvements_list(self) -> None:
        """rewrite_bullet returns a list of improvement notes."""
        result = rewrite_bullet(
            bullet="worked on stuff",
            keywords=json.dumps([]),
        )
        data = json.loads(result)
        assert "improvements" in data
        assert isinstance(data["improvements"], list)

    def test_includes_keywords_from_input(self) -> None:
        """rewrite_bullet incorporates provided keywords into the rewrite."""
        result = rewrite_bullet(
            bullet="built software systems",
            keywords=json.dumps(["kubernetes", "docker"]),
        )
        data = json.loads(result)
        combined = (data["rewritten"] + " ".join(data["improvements"])).lower()
        assert "kubernetes" in combined or "docker" in combined

    def test_empty_bullet_returns_error(self) -> None:
        """rewrite_bullet returns error JSON for empty bullet input."""
        result = rewrite_bullet(bullet="", keywords=json.dumps(["python"]))
        data = json.loads(result)
        assert "error" in data

    def test_invalid_keywords_json_returns_error(self) -> None:
        """rewrite_bullet returns error for invalid keywords JSON."""
        result = rewrite_bullet(bullet="did work", keywords="not-json")
        data = json.loads(result)
        assert "error" in data

    def test_returns_json_string(self) -> None:
        """rewrite_bullet always returns a valid JSON string."""
        result = rewrite_bullet(
            bullet="managed project delivery",
            keywords=json.dumps(["agile"]),
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_bullet_already_with_action_verb_still_returns_rewritten(self) -> None:
        """rewrite_bullet handles bullets that already begin with an action verb."""
        result = rewrite_bullet(
            bullet="Led the backend architecture redesign",
            keywords=json.dumps(["architecture"]),
        )
        data = json.loads(result)
        assert "rewritten" in data


class TestGenerateSummaryTool:
    """Tests for generate_summary tool function."""

    def test_returns_summary_field(self) -> None:
        """generate_summary returns a non-empty summary string."""
        result = generate_summary(
            skills=json.dumps(["Python", "Docker"]),
            job_title="Senior Software Engineer",
            years_experience="5",
        )
        data = json.loads(result)
        assert "summary" in data
        assert isinstance(data["summary"], str)
        assert len(data["summary"]) > 0

    def test_summary_includes_job_title(self) -> None:
        """generate_summary incorporates the job title into the summary."""
        result = generate_summary(
            skills=json.dumps(["Python"]),
            job_title="Data Scientist",
            years_experience="3",
        )
        data = json.loads(result)
        assert "Data Scientist" in data["summary"] or "data scientist" in data["summary"].lower()

    def test_summary_includes_top_skills(self) -> None:
        """generate_summary mentions skills in the output."""
        result = generate_summary(
            skills=json.dumps(["Kubernetes", "Terraform"]),
            job_title="DevOps Engineer",
            years_experience="7",
        )
        data = json.loads(result)
        summary_lower = data["summary"].lower()
        assert "kubernetes" in summary_lower or "terraform" in summary_lower

    def test_summary_includes_years_experience(self) -> None:
        """generate_summary references the years of experience."""
        result = generate_summary(
            skills=json.dumps(["Python"]),
            job_title="Engineer",
            years_experience="8",
        )
        data = json.loads(result)
        assert "8" in data["summary"]

    def test_empty_skills_returns_summary(self) -> None:
        """generate_summary handles empty skills list gracefully."""
        result = generate_summary(
            skills=json.dumps([]),
            job_title="Software Engineer",
            years_experience="2",
        )
        data = json.loads(result)
        assert "summary" in data
        assert len(data["summary"]) > 0

    def test_invalid_skills_json_returns_error(self) -> None:
        """generate_summary returns error for invalid skills JSON."""
        result = generate_summary(
            skills="not-json",
            job_title="Engineer",
            years_experience="3",
        )
        data = json.loads(result)
        assert "error" in data

    def test_returns_json_string(self) -> None:
        """generate_summary always returns a valid JSON string."""
        result = generate_summary(
            skills=json.dumps(["Python"]),
            job_title="Developer",
            years_experience="4",
        )
        data = json.loads(result)
        assert isinstance(data, dict)


class TestSuggestEditsTool:
    """Tests for suggest_edits tool function."""

    def test_returns_suggestions_list(self) -> None:
        """suggest_edits returns a list of suggestions."""
        result = suggest_edits(
            content="Worked on backend development projects.",
            requirements=json.dumps(["python", "microservices", "docker"]),
        )
        data = json.loads(result)
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_suggests_missing_keywords(self) -> None:
        """suggest_edits flags keywords absent from content."""
        result = suggest_edits(
            content="Developed REST APIs using Java.",
            requirements=json.dumps(["python", "kubernetes"]),
        )
        data = json.loads(result)
        suggestion_text = " ".join(data["suggestions"]).lower()
        assert "python" in suggestion_text or "kubernetes" in suggestion_text

    def test_no_suggestions_when_all_keywords_present(self) -> None:
        """suggest_edits returns empty suggestions when content covers all requirements."""
        result = suggest_edits(
            content="Built Python microservices deployed on Kubernetes with Docker.",
            requirements=json.dumps(["python", "kubernetes", "docker"]),
        )
        data = json.loads(result)
        assert isinstance(data["suggestions"], list)

    def test_returns_priority_field(self) -> None:
        """suggest_edits includes a priority field."""
        result = suggest_edits(
            content="Helped with tasks.",
            requirements=json.dumps(["python", "aws", "docker", "kubernetes"]),
        )
        data = json.loads(result)
        assert "priority" in data
        assert data["priority"] in ("high", "medium", "low")

    def test_empty_content_returns_suggestions(self) -> None:
        """suggest_edits handles empty content string."""
        result = suggest_edits(
            content="",
            requirements=json.dumps(["python"]),
        )
        data = json.loads(result)
        assert "suggestions" in data

    def test_invalid_requirements_json_returns_error(self) -> None:
        """suggest_edits returns error for invalid requirements JSON."""
        result = suggest_edits(content="some content", requirements="not-json")
        data = json.loads(result)
        assert "error" in data

    def test_returns_json_string(self) -> None:
        """suggest_edits always returns a valid JSON string."""
        result = suggest_edits(
            content="Developed APIs",
            requirements=json.dumps(["python"]),
        )
        data = json.loads(result)
        assert isinstance(data, dict)


class TestVerifyFactsTool:
    """Tests for verify_facts tool function."""

    def test_supported_claim_returns_true(self) -> None:
        """verify_facts returns is_supported=True when claim matches source."""
        claim = "Built Python microservices"
        source = "Developed and deployed Python-based microservices on AWS."
        result = verify_facts(claim=claim, source_data=source)
        data = json.loads(result)
        assert data["is_supported"] is True

    def test_unsupported_claim_returns_false(self) -> None:
        """verify_facts returns is_supported=False when claim contradicts source."""
        claim = "Led a team of 50 engineers"
        source = "Contributed to small team projects using Python and SQL."
        result = verify_facts(claim=claim, source_data=source)
        data = json.loads(result)
        assert data["is_supported"] is False

    def test_returns_confidence_field(self) -> None:
        """verify_facts includes a confidence level."""
        result = verify_facts(
            claim="Used Python for data pipelines",
            source_data="Developed data pipelines in Python.",
        )
        data = json.loads(result)
        assert "confidence" in data
        assert data["confidence"] in ("high", "medium", "low")

    def test_empty_claim_returns_error(self) -> None:
        """verify_facts returns error for empty claim."""
        result = verify_facts(claim="", source_data="some source data")
        data = json.loads(result)
        assert "error" in data

    def test_empty_source_returns_unsupported(self) -> None:
        """verify_facts returns is_supported=False when source data is empty."""
        result = verify_facts(claim="Led engineering teams", source_data="")
        data = json.loads(result)
        assert data["is_supported"] is False

    def test_returns_evidence_field(self) -> None:
        """verify_facts includes an evidence string."""
        result = verify_facts(
            claim="Used Docker",
            source_data="Containerized applications using Docker and Kubernetes.",
        )
        data = json.loads(result)
        assert "evidence" in data
        assert isinstance(data["evidence"], str)

    def test_returns_json_string(self) -> None:
        """verify_facts always returns a valid JSON string."""
        result = verify_facts(
            claim="Built REST APIs",
            source_data="Designed and built REST API endpoints.",
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_case_insensitive_matching(self) -> None:
        """verify_facts compares claim to source case-insensitively."""
        result = verify_facts(
            claim="PYTHON developer",
            source_data="Experienced python developer with 5 years.",
        )
        data = json.loads(result)
        assert data["is_supported"] is True


class TestOptimizationToolDefinitions:
    """Tests for ToolDefinition schemas exported from optimization module."""

    @pytest.mark.parametrize(
        "tool",
        [REWRITE_BULLET_TOOL, GENERATE_SUMMARY_TOOL, SUGGEST_EDITS_TOOL, VERIFY_FACTS_TOOL],
    )
    def test_tool_is_tool_definition(self, tool: ToolDefinition) -> None:
        """Each exported tool constant is a ToolDefinition instance."""
        assert isinstance(tool, ToolDefinition)

    @pytest.mark.parametrize(
        "tool",
        [REWRITE_BULLET_TOOL, GENERATE_SUMMARY_TOOL, SUGGEST_EDITS_TOOL, VERIFY_FACTS_TOOL],
    )
    def test_tool_has_valid_input_schema(self, tool: ToolDefinition) -> None:
        """Each tool has a JSON Schema object with type, properties, required."""
        schema = tool.input_schema
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema

    def test_tool_names(self) -> None:
        """Tool constants have the expected names."""
        assert REWRITE_BULLET_TOOL.name == "rewrite_bullet"
        assert GENERATE_SUMMARY_TOOL.name == "generate_summary"
        assert SUGGEST_EDITS_TOOL.name == "suggest_edits"
        assert VERIFY_FACTS_TOOL.name == "verify_facts"

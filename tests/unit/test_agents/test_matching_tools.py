"""Tests for matcher agent tools.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tools are pure functions — no Claude API calls.
"""

from __future__ import annotations

import json

import pytest

from resume_builder.agents.tools.matching import (
    EXTRACT_REQUIREMENTS_TOOL,
    IDENTIFY_GAPS_TOOL,
    RANK_EXPERIENCE_TOOL,
    SCORE_MATCH_TOOL,
    extract_requirements,
    identify_gaps,
    rank_experience,
    score_match,
)
from resume_builder.models.agent import ToolDefinition


class TestExtractRequirementsTool:
    """Tests for extract_requirements tool function."""

    def test_extracts_skills_from_job_text(self) -> None:
        """extract_requirements finds tech skills in job description."""
        job_text = "We need Python and SQL expertise. AWS experience is a plus."
        result = extract_requirements(job_text=job_text)
        data = json.loads(result)
        skills = [s.lower() for s in data["required_skills"]]
        assert "python" in skills
        assert "sql" in skills

    def test_extracts_years_experience(self) -> None:
        """extract_requirements parses years of experience from job text."""
        job_text = "Requires 5+ years of software engineering experience."
        result = extract_requirements(job_text=job_text)
        data = json.loads(result)
        assert data["years_experience"] == 5

    def test_extracts_education_requirements(self) -> None:
        """extract_requirements finds education level in job text."""
        job_text = "Bachelor's degree in Computer Science or related field required."
        result = extract_requirements(job_text=job_text)
        data = json.loads(result)
        assert data["education"] is not None
        assert len(data["education"]) > 0

    def test_empty_job_text_returns_empty_requirements(self) -> None:
        """extract_requirements handles empty input gracefully."""
        result = extract_requirements(job_text="")
        data = json.loads(result)
        assert data["required_skills"] == []
        assert data["years_experience"] is None

    def test_returns_json_string(self) -> None:
        """extract_requirements always returns a valid JSON string."""
        result = extract_requirements(job_text="Software engineer needed.")
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "required_skills" in data
        assert "years_experience" in data
        assert "education" in data

    def test_no_skills_text_returns_empty_skills(self) -> None:
        """extract_requirements returns empty skills list when none found."""
        result = extract_requirements(job_text="Excellent communication skills required.")
        data = json.loads(result)
        assert isinstance(data["required_skills"], list)

    def test_extracts_multiple_skills(self) -> None:
        """extract_requirements extracts all tech skills mentioned."""
        job_text = "Must know Python, Docker, Kubernetes, and PostgreSQL."
        result = extract_requirements(job_text=job_text)
        data = json.loads(result)
        skills = [s.lower() for s in data["required_skills"]]
        assert "docker" in skills
        assert "kubernetes" in skills


class TestScoreMatchTool:
    """Tests for score_match tool function."""

    def test_perfect_match_scores_100(self) -> None:
        """score_match returns 100 when all required skills are present."""
        resume_skills = json.dumps(["python", "sql", "docker"])
        required_skills = json.dumps(["python", "sql"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert data["score"] == 100

    def test_no_match_scores_0(self) -> None:
        """score_match returns 0 when no required skills are present."""
        resume_skills = json.dumps(["java", "spring"])
        required_skills = json.dumps(["python", "django"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert data["score"] == 0

    def test_partial_match_score_in_range(self) -> None:
        """score_match returns score between 0 and 100 for partial match."""
        resume_skills = json.dumps(["python", "sql"])
        required_skills = json.dumps(["python", "sql", "docker", "kubernetes"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert 0 < data["score"] < 100

    def test_returns_matching_skills(self) -> None:
        """score_match lists the skills that matched."""
        resume_skills = json.dumps(["python", "sql", "java"])
        required_skills = json.dumps(["python", "sql", "docker"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        matched = [s.lower() for s in data["matching_skills"]]
        assert "python" in matched
        assert "sql" in matched
        assert "java" not in matched

    def test_returns_total_required_count(self) -> None:
        """score_match includes total number of required skills."""
        resume_skills = json.dumps(["python"])
        required_skills = json.dumps(["python", "sql", "docker"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert data["total_required"] == 3

    def test_case_insensitive_matching(self) -> None:
        """score_match compares skills case-insensitively."""
        resume_skills = json.dumps(["Python", "SQL"])
        required_skills = json.dumps(["python", "sql"])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert data["score"] == 100

    def test_empty_required_skills_scores_100(self) -> None:
        """score_match returns 100 when no skills are required."""
        resume_skills = json.dumps(["python"])
        required_skills = json.dumps([])
        result = score_match(resume_skills=resume_skills, required_skills=required_skills)
        data = json.loads(result)
        assert data["score"] == 100

    def test_invalid_json_returns_error(self) -> None:
        """score_match returns error JSON for invalid input."""
        result = score_match(resume_skills="not-json", required_skills="[]")
        data = json.loads(result)
        assert "error" in data

    def test_returns_json_string(self) -> None:
        """score_match always returns a valid JSON string."""
        result = score_match(
            resume_skills=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
        )
        data = json.loads(result)
        assert isinstance(data, dict)


class TestIdentifyGapsTool:
    """Tests for identify_gaps tool function."""

    def test_finds_missing_skills(self) -> None:
        """identify_gaps returns skills in requirements but not in resume."""
        resume_skills = json.dumps(["python", "sql"])
        required_skills = json.dumps(["python", "sql", "docker", "kubernetes"])
        result = identify_gaps(resume_skills=resume_skills, required_skills=required_skills)
        gaps = json.loads(result)
        assert "docker" in gaps
        assert "kubernetes" in gaps

    def test_no_gaps_when_all_present(self) -> None:
        """identify_gaps returns empty list when resume covers all requirements."""
        resume_skills = json.dumps(["python", "sql", "docker"])
        required_skills = json.dumps(["python", "sql"])
        result = identify_gaps(resume_skills=resume_skills, required_skills=required_skills)
        gaps = json.loads(result)
        assert gaps == []

    def test_case_insensitive(self) -> None:
        """identify_gaps compares skills case-insensitively."""
        resume_skills = json.dumps(["Python", "SQL"])
        required_skills = json.dumps(["python", "sql", "docker"])
        result = identify_gaps(resume_skills=resume_skills, required_skills=required_skills)
        gaps = json.loads(result)
        assert "docker" in gaps
        assert "python" not in [g.lower() for g in gaps]

    def test_empty_resume_skills_all_required_are_gaps(self) -> None:
        """identify_gaps returns all required when resume has no skills."""
        resume_skills = json.dumps([])
        required_skills = json.dumps(["python", "sql"])
        result = identify_gaps(resume_skills=resume_skills, required_skills=required_skills)
        gaps = json.loads(result)
        assert len(gaps) == 2

    def test_returns_json_string(self) -> None:
        """identify_gaps always returns a valid JSON string."""
        result = identify_gaps(
            resume_skills=json.dumps(["python"]),
            required_skills=json.dumps(["python", "sql"]),
        )
        gaps = json.loads(result)
        assert isinstance(gaps, list)

    def test_invalid_json_returns_error(self) -> None:
        """identify_gaps returns error JSON for invalid input."""
        result = identify_gaps(resume_skills="not-json", required_skills="[]")
        data = json.loads(result)
        assert "error" in data


class TestRankExperienceTool:
    """Tests for rank_experience tool function."""

    def test_ranks_most_relevant_first(self) -> None:
        """rank_experience returns positions ordered by keyword relevance."""
        positions = json.dumps(
            [
                {"title": "Java Developer", "description": "Built Java Spring applications"},
                {
                    "title": "Python Engineer",
                    "description": "Built Python microservices with Docker",
                },
            ]
        )
        keywords = json.dumps(["python", "docker"])
        result = rank_experience(positions=positions, keywords=keywords)
        ranked = json.loads(result)
        assert ranked[0]["title"] == "Python Engineer"

    def test_returns_all_positions(self) -> None:
        """rank_experience returns all positions, not just top matches."""
        positions = json.dumps(
            [
                {"title": "Role A", "description": "Python work"},
                {"title": "Role B", "description": "Java work"},
                {"title": "Role C", "description": "SQL work"},
            ]
        )
        keywords = json.dumps(["python"])
        result = rank_experience(positions=positions, keywords=keywords)
        ranked = json.loads(result)
        assert len(ranked) == 3

    def test_includes_match_score(self) -> None:
        """rank_experience includes a relevance score for each position."""
        positions = json.dumps([{"title": "Engineer", "description": "Python and SQL developer"}])
        keywords = json.dumps(["python"])
        result = rank_experience(positions=positions, keywords=keywords)
        ranked = json.loads(result)
        assert "score" in ranked[0]

    def test_empty_positions_returns_empty(self) -> None:
        """rank_experience returns empty list for empty positions input."""
        result = rank_experience(positions=json.dumps([]), keywords=json.dumps(["python"]))
        ranked = json.loads(result)
        assert ranked == []

    def test_returns_json_string(self) -> None:
        """rank_experience always returns a valid JSON string."""
        positions = json.dumps([{"title": "Dev", "description": "Python"}])
        result = rank_experience(positions=positions, keywords=json.dumps(["python"]))
        ranked = json.loads(result)
        assert isinstance(ranked, list)

    def test_invalid_json_returns_error(self) -> None:
        """rank_experience returns error JSON for invalid input."""
        result = rank_experience(positions="not-json", keywords="[]")
        data = json.loads(result)
        assert "error" in data


class TestMatchingToolDefinitions:
    """Tests for ToolDefinition schemas exported from matching module."""

    @pytest.mark.parametrize(
        "tool",
        [EXTRACT_REQUIREMENTS_TOOL, SCORE_MATCH_TOOL, IDENTIFY_GAPS_TOOL, RANK_EXPERIENCE_TOOL],
    )
    def test_tool_is_tool_definition(self, tool: ToolDefinition) -> None:
        """Each exported tool constant is a ToolDefinition instance."""
        assert isinstance(tool, ToolDefinition)

    @pytest.mark.parametrize(
        "tool",
        [EXTRACT_REQUIREMENTS_TOOL, SCORE_MATCH_TOOL, IDENTIFY_GAPS_TOOL, RANK_EXPERIENCE_TOOL],
    )
    def test_tool_has_valid_input_schema(self, tool: ToolDefinition) -> None:
        """Each tool has a JSON Schema object with type, properties, required."""
        schema = tool.input_schema
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema

    def test_tool_names(self) -> None:
        """Tool constants have the expected names."""
        assert EXTRACT_REQUIREMENTS_TOOL.name == "extract_requirements"
        assert SCORE_MATCH_TOOL.name == "score_match"
        assert IDENTIFY_GAPS_TOOL.name == "identify_gaps"
        assert RANK_EXPERIENCE_TOOL.name == "rank_experience"

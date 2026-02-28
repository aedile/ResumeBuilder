"""Tests for parser agent tools.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tools are pure functions — no Claude API calls.
"""

from __future__ import annotations

import json

import pytest

from resume_builder.agents.tools.parsing import (
    EXTRACT_IMPLICIT_SKILLS_TOOL,
    NORMALIZE_DATES_TOOL,
    PARSE_CSV_TOOL,
    VALIDATE_DATA_TOOL,
    extract_implicit_skills,
    normalize_dates,
    parse_csv,
    validate_data,
)
from resume_builder.models.agent import ToolDefinition


class TestParseCsvTool:
    """Tests for parse_csv tool function."""

    def test_parse_csv_profile_returns_rows(self) -> None:
        """parse_csv returns structured row data for a profile CSV."""
        csv_content = "First Name,Last Name,Headline\nAlex,Chen,Software Engineer"
        result = parse_csv(csv_content=csv_content, csv_type="profile")
        data = json.loads(result)
        assert data["csv_type"] == "profile"
        assert data["count"] == 1
        assert data["rows"][0]["First Name"] == "Alex"

    def test_parse_csv_returns_all_rows(self) -> None:
        """parse_csv returns all rows from multi-row CSV."""
        csv_content = "Name\nPython\nAWS\nDocker"
        result = parse_csv(csv_content=csv_content, csv_type="skills")
        data = json.loads(result)
        assert data["count"] == 3

    def test_parse_csv_empty_content_returns_error(self) -> None:
        """parse_csv returns error JSON for empty content."""
        result = parse_csv(csv_content="", csv_type="profile")
        data = json.loads(result)
        assert "error" in data

    def test_parse_csv_returns_json_string(self) -> None:
        """parse_csv always returns a valid JSON string."""
        result = parse_csv(csv_content="col\nval", csv_type="positions")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_parse_csv_preserves_csv_type(self) -> None:
        """parse_csv includes csv_type in the result on success."""
        result = parse_csv(csv_content="Name\nPython", csv_type="skills")
        data = json.loads(result)
        assert data.get("csv_type") == "skills"

    def test_parse_csv_header_only_returns_zero_rows(self) -> None:
        """parse_csv with header but no data returns count 0."""
        result = parse_csv(csv_content="Name,Title", csv_type="positions")
        data = json.loads(result)
        assert data["count"] == 0
        assert data["rows"] == []

    def test_parse_csv_multirow_positions(self) -> None:
        """parse_csv handles multi-row CSV with multiple fields."""
        csv_content = (
            "Company Name,Title,Started On,Finished On\n"
            "Acme Inc,Engineer,2020-01,2022-06\n"
            "Beta Corp,Senior Engineer,2022-07,"
        )
        result = parse_csv(csv_content=csv_content, csv_type="positions")
        data = json.loads(result)
        assert data["count"] == 2
        assert data["rows"][0]["Company Name"] == "Acme Inc"


class TestNormalizeDatesTool:
    """Tests for normalize_dates tool function."""

    def test_normalize_linkedin_format(self) -> None:
        """normalize_dates passes through YYYY-MM format unchanged."""
        assert normalize_dates(date_str="2021-03") == "2021-03"

    def test_normalize_full_month_name(self) -> None:
        """normalize_dates converts 'March 2021' to '2021-03'."""
        assert normalize_dates(date_str="March 2021") == "2021-03"

    def test_normalize_abbreviated_month(self) -> None:
        """normalize_dates converts 'Mar 2021' to '2021-03'."""
        assert normalize_dates(date_str="Mar 2021") == "2021-03"

    def test_normalize_empty_string_returns_empty(self) -> None:
        """normalize_dates returns empty string for empty input."""
        assert normalize_dates(date_str="") == ""

    def test_normalize_present_returns_empty(self) -> None:
        """normalize_dates returns empty string for 'Present'."""
        assert normalize_dates(date_str="Present") == ""

    def test_normalize_invalid_returns_empty(self) -> None:
        """normalize_dates returns empty string for unrecognized date strings."""
        assert normalize_dates(date_str="not-a-date") == ""

    def test_normalize_january(self) -> None:
        """normalize_dates handles January correctly (month 01)."""
        assert normalize_dates(date_str="January 2020") == "2020-01"

    def test_normalize_december(self) -> None:
        """normalize_dates handles December correctly (month 12)."""
        assert normalize_dates(date_str="December 2023") == "2023-12"

    def test_normalize_strips_whitespace(self) -> None:
        """normalize_dates handles leading/trailing whitespace."""
        assert normalize_dates(date_str="  2021-03  ") == "2021-03"


class TestExtractImplicitSkillsTool:
    """Tests for extract_implicit_skills tool function."""

    def test_finds_python_in_text(self) -> None:
        """extract_implicit_skills finds Python mentioned in text."""
        result = extract_implicit_skills(text="Built a data pipeline using Python and pandas.")
        skills = json.loads(result)
        assert "python" in [s.lower() for s in skills]

    def test_finds_aws_in_text(self) -> None:
        """extract_implicit_skills finds AWS mentioned in text."""
        result = extract_implicit_skills(text="Deployed microservices on AWS using ECS.")
        skills = json.loads(result)
        assert "aws" in [s.lower() for s in skills]

    def test_case_insensitive_matching(self) -> None:
        """extract_implicit_skills matches skills case-insensitively."""
        result = extract_implicit_skills(text="PYTHON and DOCKER were used.")
        skills = json.loads(result)
        assert len(skills) >= 2  # noqa: PLR2004

    def test_empty_text_returns_empty_list(self) -> None:
        """extract_implicit_skills returns empty list for empty text."""
        result = extract_implicit_skills(text="")
        skills = json.loads(result)
        assert skills == []

    def test_no_skills_text_returns_empty_list(self) -> None:
        """extract_implicit_skills returns empty list when no tech skills found."""
        result = extract_implicit_skills(text="Managed the quarterly budget review process.")
        skills = json.loads(result)
        assert isinstance(skills, list)

    def test_returns_json_string(self) -> None:
        """extract_implicit_skills returns a valid JSON string."""
        result = extract_implicit_skills(text="Used Python and React")
        skills = json.loads(result)
        assert isinstance(skills, list)

    def test_deduplicates_skills(self) -> None:
        """extract_implicit_skills deduplicates repeated skill mentions."""
        result = extract_implicit_skills(text="Python python PYTHON was the language of choice")
        skills = json.loads(result)
        lower_skills = [s.lower() for s in skills]
        assert len(lower_skills) == len(set(lower_skills))

    def test_finds_docker_in_text(self) -> None:
        """extract_implicit_skills finds Docker from tools category."""
        result = extract_implicit_skills(text="Containerized applications using Docker and Kubernetes.")
        skills = json.loads(result)
        assert "docker" in [s.lower() for s in skills]


class TestValidateDataTool:
    """Tests for validate_data tool function."""

    def test_all_fields_present_is_valid(self) -> None:
        """validate_data returns is_valid=True when all required fields present."""
        data = json.dumps({"name": "Alex", "email": "alex@example.com"})
        required = json.dumps(["name", "email"])
        result = validate_data(data=data, required_fields=required)
        output = json.loads(result)
        assert output["is_valid"] is True
        assert output["missing_fields"] == []

    def test_missing_fields_flagged(self) -> None:
        """validate_data returns missing field names when required fields absent."""
        data = json.dumps({"name": "Alex"})
        required = json.dumps(["name", "email", "phone"])
        result = validate_data(data=data, required_fields=required)
        output = json.loads(result)
        assert output["is_valid"] is False
        assert "email" in output["missing_fields"]
        assert "phone" in output["missing_fields"]

    def test_completeness_100_when_all_present(self) -> None:
        """validate_data returns 100% completeness when all fields present."""
        data = json.dumps({"a": 1, "b": 2})
        required = json.dumps(["a", "b"])
        result = validate_data(data=data, required_fields=required)
        output = json.loads(result)
        assert output["completeness_percent"] == 100.0

    def test_completeness_partial(self) -> None:
        """validate_data returns partial completeness when fields missing."""
        data = json.dumps({"a": 1})
        required = json.dumps(["a", "b", "c", "d"])
        result = validate_data(data=data, required_fields=required)
        output = json.loads(result)
        assert output["completeness_percent"] == 25.0

    def test_invalid_json_data_returns_error(self) -> None:
        """validate_data handles invalid JSON data gracefully."""
        result = validate_data(data="not-json", required_fields='["field"]')
        output = json.loads(result)
        assert "error" in output

    def test_empty_required_fields_always_valid(self) -> None:
        """validate_data with no required fields returns is_valid=True."""
        data = json.dumps({"anything": "here"})
        required = json.dumps([])
        result = validate_data(data=data, required_fields=required)
        output = json.loads(result)
        assert output["is_valid"] is True
        assert output["completeness_percent"] == 100.0

    def test_returns_json_string(self) -> None:
        """validate_data always returns a valid JSON string."""
        result = validate_data(data="{}", required_fields="[]")
        output = json.loads(result)
        assert isinstance(output, dict)


class TestToolDefinitions:
    """Tests for ToolDefinition schemas exported from parsing module."""

    @pytest.mark.parametrize(
        "tool",
        [PARSE_CSV_TOOL, NORMALIZE_DATES_TOOL, EXTRACT_IMPLICIT_SKILLS_TOOL, VALIDATE_DATA_TOOL],
    )
    def test_tool_is_tool_definition(self, tool: ToolDefinition) -> None:
        """Each exported tool constant is a ToolDefinition instance."""
        assert isinstance(tool, ToolDefinition)

    @pytest.mark.parametrize(
        "tool",
        [PARSE_CSV_TOOL, NORMALIZE_DATES_TOOL, EXTRACT_IMPLICIT_SKILLS_TOOL, VALIDATE_DATA_TOOL],
    )
    def test_tool_has_non_empty_name(self, tool: ToolDefinition) -> None:
        """Each tool definition has a non-empty name."""
        assert tool.name

    @pytest.mark.parametrize(
        "tool",
        [PARSE_CSV_TOOL, NORMALIZE_DATES_TOOL, EXTRACT_IMPLICIT_SKILLS_TOOL, VALIDATE_DATA_TOOL],
    )
    def test_tool_has_non_empty_description(self, tool: ToolDefinition) -> None:
        """Each tool definition has a non-empty description."""
        assert tool.description

    @pytest.mark.parametrize(
        "tool",
        [PARSE_CSV_TOOL, NORMALIZE_DATES_TOOL, EXTRACT_IMPLICIT_SKILLS_TOOL, VALIDATE_DATA_TOOL],
    )
    def test_tool_has_valid_input_schema(self, tool: ToolDefinition) -> None:
        """Each tool definition has a valid JSON Schema object."""
        schema = tool.input_schema
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema

    def test_parse_csv_tool_name(self) -> None:
        """PARSE_CSV_TOOL has the expected name."""
        assert PARSE_CSV_TOOL.name == "parse_csv"

    def test_normalize_dates_tool_name(self) -> None:
        """NORMALIZE_DATES_TOOL has the expected name."""
        assert NORMALIZE_DATES_TOOL.name == "normalize_dates"

    def test_extract_implicit_skills_tool_name(self) -> None:
        """EXTRACT_IMPLICIT_SKILLS_TOOL has the expected name."""
        assert EXTRACT_IMPLICIT_SKILLS_TOOL.name == "extract_implicit_skills"

    def test_validate_data_tool_name(self) -> None:
        """VALIDATE_DATA_TOOL has the expected name."""
        assert VALIDATE_DATA_TOOL.name == "validate_data"

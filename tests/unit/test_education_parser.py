"""Tests for Education CSV parser.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

from pathlib import Path

import pytest

from resume_builder.parsers.education import parse_education


class TestEducationParser:
    """Tests for parse_education function."""

    def test_parse_valid_education_csv(self, tmp_path: Path) -> None:
        """Parse valid Education.csv correctly."""
        csv_content = """School Name,Start Date,End Date,Degree Name,Activities
Stanford University,2010,2012,MS Computer Science,Graduate ML coursework
UC Berkeley,2006,2010,BS Mathematics,Undergraduate research
"""
        csv_file = tmp_path / "education.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        education = parse_education(csv_file)

        assert len(education) == 2
        assert education[0].school_name == "Stanford University"
        assert education[0].degree_name == "MS Computer Science"
        assert education[0].start_year == 2010
        assert education[0].end_year == 2012
        assert education[1].school_name == "UC Berkeley"

    def test_parse_education_missing_file_returns_empty(self) -> None:
        """Return empty list when CSV file doesn't exist."""
        nonexistent = Path("/nonexistent/education.csv")

        education = parse_education(nonexistent)

        assert education == []

    def test_parse_education_empty_csv(self, tmp_path: Path) -> None:
        """Return empty list for CSV with only headers."""
        csv_content = "School Name,Start Date,End Date,Degree Name,Activities\n"
        csv_file = tmp_path / "education.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        education = parse_education(csv_file)

        assert education == []

    def test_parse_education_invalid_csv(self, tmp_path: Path) -> None:
        """Handle malformed CSV gracefully."""
        csv_content = "Not a valid CSV\nMissing headers"
        csv_file = tmp_path / "education.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        with pytest.raises(ValueError, match="Missing required field"):
            parse_education(csv_file)

    def test_parse_education_with_current_study(self, tmp_path: Path) -> None:
        """Handle ongoing education (no end date)."""
        csv_content = """School Name,Start Date,End Date,Degree Name,Activities
MIT,2023,,PhD Computer Science,Currently pursuing doctorate
"""
        csv_file = tmp_path / "education.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        education = parse_education(csv_file)

        assert len(education) == 1
        assert education[0].end_year is None

    def test_parse_education_year_parsing(self, tmp_path: Path) -> None:
        """Parse year-only dates correctly."""
        csv_content = """School Name,Start Date,End Date,Degree Name,Activities
Test University,2015,2019,BS Degree,Test activities
"""
        csv_file = tmp_path / "education.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        education = parse_education(csv_file)

        # Year-only should parse as integers
        assert education[0].start_year == 2015
        assert education[0].end_year == 2019

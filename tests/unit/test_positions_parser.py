"""Tests for Positions CSV parser.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

from datetime import date
from pathlib import Path

import pytest

from resume_builder.parsers.positions import _parse_linkedin_date, parse_positions


class TestPositionsParser:
    """Tests for parse_positions function."""

    def test_parse_valid_positions_csv(self, tmp_path: Path) -> None:
        """Parse valid Positions.csv correctly."""
        csv_content = """Company Name,Title,Description,Location,Started On,Finished On
TechVision AI,Staff ML Engineer,Leading ML infrastructure,San Francisco CA,2021-03,
DataFlow Inc,Senior ML Engineer,Built ML systems,San Francisco CA,2018-01,2021-03
"""
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        positions = parse_positions(csv_file)

        assert len(positions) == 2
        # Should be sorted newest first
        assert positions[0].company == "TechVision AI"
        assert positions[0].title == "Staff ML Engineer"
        assert positions[0].start_date == date(2021, 3, 1)
        assert positions[0].end_date is None  # Current position
        assert positions[0].location == "San Francisco CA"

        assert positions[1].company == "DataFlow Inc"
        assert positions[1].start_date == date(2018, 1, 1)
        assert positions[1].end_date == date(2021, 3, 1)

    def test_parse_positions_with_current_job(self, tmp_path: Path) -> None:
        """Handle current position with empty end_date."""
        csv_content = """Company Name,Title,Description,Location,Started On,Finished On
CurrentCo,Engineer,Working here now,Remote,2023-06,
"""
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        positions = parse_positions(csv_file)

        assert len(positions) == 1
        assert positions[0].end_date is None
        assert positions[0].is_current is True

    def test_parse_positions_sorted_by_date(self, tmp_path: Path) -> None:
        """Positions are sorted by start_date descending (newest first)."""
        csv_content = """Company Name,Title,Description,Location,Started On,Finished On
OldCo,Junior Dev,Old job,NYC,2010-01,2012-01
MiddleCo,Senior Dev,Middle job,NYC,2015-06,2018-12
NewCo,Staff Dev,New job,NYC,2020-01,
"""
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        positions = parse_positions(csv_file)

        assert len(positions) == 3
        assert positions[0].company == "NewCo"  # 2020-01
        assert positions[1].company == "MiddleCo"  # 2015-06
        assert positions[2].company == "OldCo"  # 2010-01

    def test_parse_positions_preserves_multiline_description(self, tmp_path: Path) -> None:
        """Preserve newlines in multiline descriptions."""
        csv_content = """Company Name,Title,Description,Location,Started On,Finished On
TestCo,Engineer,"Line 1
Line 2
Line 3",Remote,2020-01,2021-01
"""
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        positions = parse_positions(csv_file)

        assert len(positions) == 1
        assert "Line 1\nLine 2\nLine 3" in positions[0].description

    def test_parse_positions_missing_file_returns_empty_list(self) -> None:
        """Return empty list when CSV file does not exist (graceful degradation)."""
        nonexistent = Path("/nonexistent/positions.csv")

        result = parse_positions(nonexistent)

        assert result == []

    def test_parse_positions_invalid_csv(self, tmp_path: Path) -> None:
        """Handle malformed CSV gracefully."""
        csv_content = "Not a valid CSV\nMissing headers"
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        with pytest.raises(ValueError, match="Missing required fields"):
            parse_positions(csv_file)

    def test_parse_positions_empty_csv(self, tmp_path: Path) -> None:
        """Return empty list for CSV with only headers."""
        csv_content = "Company Name,Title,Description,Location,Started On,Finished On\n"
        csv_file = tmp_path / "positions.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        positions = parse_positions(csv_file)

        assert positions == []


class TestLinkedInDateParser:
    """Tests for _parse_linkedin_date helper function."""

    def test_parse_linkedin_date_valid(self) -> None:
        """Parse valid YYYY-MM format to first day of month."""
        assert _parse_linkedin_date("2021-03") == date(2021, 3, 1)
        assert _parse_linkedin_date("2020-12") == date(2020, 12, 1)
        assert _parse_linkedin_date("2019-01") == date(2019, 1, 1)

    def test_parse_linkedin_date_empty(self) -> None:
        """Return None for empty string."""
        assert _parse_linkedin_date("") is None
        assert _parse_linkedin_date("   ") is None

    def test_parse_linkedin_date_invalid_format(self) -> None:
        """Return None for invalid date format."""
        assert _parse_linkedin_date("2021") is None
        assert _parse_linkedin_date("2021-13") is None  # Invalid month
        assert _parse_linkedin_date("invalid") is None
        assert _parse_linkedin_date("21-03") is None  # Wrong year format

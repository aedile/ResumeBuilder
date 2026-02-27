"""Tests for Profile CSV parser.

TDD RED phase: Define requirements for parsing LinkedIn Profile.csv
"""

from pathlib import Path

import pytest

from resume_builder.exceptions import ParseError, ResumeBuilderError
from resume_builder.models.resume import Profile
from resume_builder.parsers.profile import parse_profile


class TestProfileParser:
    """Tests for parse_profile function."""

    def test_parse_valid_profile_csv(self, tmp_path: Path) -> None:
        """Parser extracts profile data from valid CSV."""
        csv_content = (
            "First Name,Last Name,Maiden Name,Address,Birth Date,Headline,"
            "Summary,Industry,Zip Code,Geo Location,Twitter Handles,Websites,"
            "Instant Messengers\n"
            "John,Doe,,123 Main St,01/15/1990,Software Engineer,"
            'Experienced developer,Technology,12345,"San Francisco, CA",,'
            "https://johndoe.com,\n"
        )
        csv_file = tmp_path / "Profile.csv"
        csv_file.write_text(csv_content)

        profile = parse_profile(csv_file)

        assert isinstance(profile, Profile)
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.headline == "Software Engineer"
        assert profile.summary == "Experienced developer"
        assert profile.industry == "Technology"
        assert profile.location == "San Francisco, CA"

    def test_parse_profile_with_missing_optional_fields(self, tmp_path: Path) -> None:
        """Parser handles missing optional fields."""
        csv_content = (
            "First Name,Last Name,Maiden Name,Address,Birth Date,Headline,"
            "Summary,Industry,Zip Code,Geo Location,Twitter Handles,Websites,"
            "Instant Messengers\n"
            "Jane,Smith,,,,Senior Developer,,,,,,https://janesmith.com,\n"
        )
        csv_file = tmp_path / "Profile.csv"
        csv_file.write_text(csv_content)

        profile = parse_profile(csv_file)

        assert profile.first_name == "Jane"
        assert profile.last_name == "Smith"
        assert profile.headline == "Senior Developer"
        assert profile.summary is None
        assert profile.industry is None
        assert profile.location is None

    def test_parse_profile_file_not_found_raises_parse_error(self) -> None:
        """Parser raises ParseError for missing file."""
        with pytest.raises(ParseError):
            parse_profile(Path("nonexistent.csv"))

    def test_parse_profile_empty_csv_raises_parse_error(self, tmp_path: Path) -> None:
        """Parser raises ParseError for CSV with no data rows."""
        csv_file = tmp_path / "Profile.csv"
        csv_file.write_text("Invalid,CSV,Data\n")

        with pytest.raises(ParseError, match="empty"):
            parse_profile(csv_file)

    def test_parse_profile_missing_fields_raises_parse_error(self, tmp_path: Path) -> None:
        """Parser raises ParseError when required fields are absent from row."""
        csv_file = tmp_path / "Profile.csv"
        csv_file.write_text("First Name,Last Name,Headline\n,,\n")

        with pytest.raises(ParseError, match="Missing required fields"):
            parse_profile(csv_file)

    def test_parse_error_is_resume_builder_error(self) -> None:
        """ParseError is catchable as ResumeBuilderError."""
        with pytest.raises(ResumeBuilderError):
            parse_profile(Path("nonexistent.csv"))

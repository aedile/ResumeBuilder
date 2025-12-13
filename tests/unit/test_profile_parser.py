"""Tests for Profile CSV parser.

TDD RED phase: Define requirements for parsing LinkedIn Profile.csv
"""

from pathlib import Path

import pytest

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

    def test_parse_profile_file_not_found(self) -> None:
        """Parser raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_profile(Path("nonexistent.csv"))

    def test_parse_profile_invalid_csv(self, tmp_path: Path) -> None:
        """Parser raises ValueError for invalid CSV format."""
        csv_file = tmp_path / "Profile.csv"
        csv_file.write_text("Invalid,CSV,Data\n")

        with pytest.raises(ValueError, match="empty"):
            parse_profile(csv_file)

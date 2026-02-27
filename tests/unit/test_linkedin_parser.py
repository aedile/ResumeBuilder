"""Tests for LinkedIn export parser orchestrator.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

from pathlib import Path

import pytest

from resume_builder.exceptions import ExportNotFoundError, InvalidExportError, ResumeBuilderError
from resume_builder.models.resume import Resume
from resume_builder.parsers.linkedin import parse_linkedin_export


class TestLinkedInParserOrchestrator:
    """Tests for parse_linkedin_export function."""

    def test_parse_complete_export(self, tmp_path: Path) -> None:
        """Parse complete LinkedIn export directory to Resume object."""
        # Create minimal CSV files
        (tmp_path / "Profile.csv").write_text(
            "First Name,Last Name,Headline\nJohn,Doe,Engineer\n",
            encoding="utf-8",
        )
        (tmp_path / "Positions.csv").write_text(
            "Company Name,Title,Started On,Finished On,Description,Location\n"
            "TechCorp,Engineer,2020-01,2023-12,Built systems,SF\n",
            encoding="utf-8",
        )
        (tmp_path / "Education.csv").write_text(
            "School Name,Start Date,End Date,Degree Name,Activities\n"
            "MIT,2015,2019,BS CS,Research\n",
            encoding="utf-8",
        )
        (tmp_path / "Skills.csv").write_text("Name\nPython\nDocker\n", encoding="utf-8")

        resume = parse_linkedin_export(tmp_path)

        assert isinstance(resume, Resume)
        assert resume.profile.first_name == "John"
        assert len(resume.positions) == 1
        assert len(resume.education) == 1
        assert len(resume.skills) == 2

    def test_parse_partial_export_missing_optional(self, tmp_path: Path) -> None:
        """Handle missing optional CSV files gracefully."""
        # Only Profile.csv (required)
        (tmp_path / "Profile.csv").write_text(
            "First Name,Last Name,Headline\nJane,Smith,Designer\n",
            encoding="utf-8",
        )

        resume = parse_linkedin_export(tmp_path)

        assert resume.profile.first_name == "Jane"
        assert resume.positions == []
        assert resume.education == []
        assert resume.skills == []

    def test_parse_missing_profile_raises_invalid_export_error(self, tmp_path: Path) -> None:
        """Raise InvalidExportError if required Profile.csv is missing."""
        # No Profile.csv
        (tmp_path / "Skills.csv").write_text("Name\nPython\n", encoding="utf-8")

        with pytest.raises(InvalidExportError, match=r"Profile\.csv is required"):
            parse_linkedin_export(tmp_path)

    def test_parse_invalid_directory_raises_export_not_found_error(self) -> None:
        """Raise ExportNotFoundError if directory doesn't exist."""
        nonexistent = Path("/nonexistent/linkedin/export")

        with pytest.raises(ExportNotFoundError, match="Directory not found"):
            parse_linkedin_export(nonexistent)

    def test_export_not_found_is_resume_builder_error(self) -> None:
        """ExportNotFoundError is catchable as ResumeBuilderError."""
        nonexistent = Path("/nonexistent/linkedin/export")

        with pytest.raises(ResumeBuilderError):
            parse_linkedin_export(nonexistent)

    def test_invalid_export_is_resume_builder_error(self, tmp_path: Path) -> None:
        """InvalidExportError is catchable as ResumeBuilderError."""
        with pytest.raises(ResumeBuilderError):
            parse_linkedin_export(tmp_path)

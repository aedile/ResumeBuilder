"""Tests for Skills CSV parser.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

from pathlib import Path

import pytest

from resume_builder.parsers.skills import _categorize_skill, parse_skills


class TestSkillsParser:
    """Tests for parse_skills function."""

    def test_parse_valid_skills_csv(self, tmp_path: Path) -> None:
        """Parse valid Skills.csv correctly."""
        csv_content = """Name
Python
JavaScript
Machine Learning
"""
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        skills = parse_skills(csv_file)

        assert len(skills) == 3
        assert skills[0].name == "Python"
        assert skills[1].name == "JavaScript"
        assert skills[2].name == "Machine Learning"
        # Without categorization, all categories should be None
        assert all(s.category is None for s in skills)

    def test_parse_skills_removes_duplicates(self, tmp_path: Path) -> None:
        """Remove duplicate skills (case-insensitive)."""
        csv_content = """Name
Python
python
PYTHON
JavaScript
javascript
"""
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        skills = parse_skills(csv_file)

        assert len(skills) == 2  # Python and JavaScript (deduplicated)
        skill_names = [s.name.lower() for s in skills]
        assert "python" in skill_names
        assert "javascript" in skill_names

    def test_parse_skills_empty_csv(self, tmp_path: Path) -> None:
        """Return empty list for CSV with only headers."""
        csv_content = "Name\n"
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        skills = parse_skills(csv_file)

        assert skills == []

    def test_parse_skills_missing_file_returns_empty_list(self) -> None:
        """Return empty list when CSV file does not exist (graceful degradation)."""
        nonexistent = Path("/nonexistent/skills.csv")

        result = parse_skills(nonexistent)

        assert result == []

    def test_parse_skills_invalid_csv(self, tmp_path: Path) -> None:
        """Handle malformed CSV gracefully."""
        csv_content = "Not a valid CSV\nMissing Name header"
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        with pytest.raises(ValueError, match="Missing required field"):
            parse_skills(csv_file)

    def test_parse_skills_with_categorization(self, tmp_path: Path) -> None:
        """Auto-categorize skills when enabled."""
        csv_content = """Name
Python
Django
AWS
Docker
"""
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        skills = parse_skills(csv_file, categorize=True)

        assert len(skills) == 4
        # Verify categorization happened
        python_skill = next(s for s in skills if s.name == "Python")
        assert python_skill.category is not None
        assert "Programming" in python_skill.category or "Language" in python_skill.category

    def test_parse_skills_without_categorization(self, tmp_path: Path) -> None:
        """No categories when categorization disabled."""
        csv_content = """Name
Python
Django
AWS
"""
        csv_file = tmp_path / "skills.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        skills = parse_skills(csv_file, categorize=False)

        # All categories should be None when categorize=False
        assert all(s.category is None for s in skills)


class TestSkillCategorization:
    """Tests for _categorize_skill helper function."""

    def test_categorize_programming_languages(self) -> None:
        """Categorize common programming languages."""
        assert _categorize_skill("Python") == "Programming Languages"
        assert _categorize_skill("Java") == "Programming Languages"
        assert _categorize_skill("JavaScript") == "Programming Languages"
        assert _categorize_skill("TypeScript") == "Programming Languages"
        assert _categorize_skill("Go") == "Programming Languages"

    def test_categorize_frameworks(self) -> None:
        """Categorize common frameworks."""
        assert _categorize_skill("Django") == "Frameworks"
        assert _categorize_skill("React") == "Frameworks"
        assert _categorize_skill("TensorFlow") == "Frameworks"
        assert _categorize_skill("PyTorch") == "Frameworks"
        assert _categorize_skill("Flask") == "Frameworks"

    def test_categorize_cloud_platforms(self) -> None:
        """Categorize cloud platforms."""
        assert _categorize_skill("AWS") == "Cloud Platforms"
        assert _categorize_skill("Google Cloud Platform") == "Cloud Platforms"
        assert _categorize_skill("GCP") == "Cloud Platforms"
        assert _categorize_skill("Azure") == "Cloud Platforms"

    def test_categorize_unknown_skill(self) -> None:
        """Return None for skills that don't match known categories."""
        assert _categorize_skill("Unknown Skill XYZ") is None
        assert _categorize_skill("Custom Framework 2024") is None

    def test_categorize_case_insensitive(self) -> None:
        """Categorization is case-insensitive."""
        assert _categorize_skill("python") == "Programming Languages"
        assert _categorize_skill("PYTHON") == "Programming Languages"
        assert _categorize_skill("PyThOn") == "Programming Languages"

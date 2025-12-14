"""Tests for HTML generator.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

from datetime import date

import pytest

from resume_builder.generators.html import HTMLGenerator
from resume_builder.models.resume import Position, Profile, Resume, Skill


@pytest.fixture
def sample_resume() -> Resume:
    """Create sample Resume for generator testing."""
    return Resume(
        profile=Profile(
            first_name="Alice",
            last_name="Johnson",
            headline="Product Manager",
        ),
        positions=[
            Position(
                company="StartupCo",
                title="Product Manager",
                start_date=date(2021, 3, 1),
                description="Led product development",
            )
        ],
        education=[],
        skills=[
            Skill(name="Product Management"),
            Skill(name="Agile"),
        ],
        certifications=[],
        projects=[],
        publications=[],
        languages=[],
        honors=[],
        volunteer=[],
    )


class TestHTMLGenerator:
    """Tests for HTMLGenerator class."""

    def test_generate_html_classic(self, sample_resume: Resume) -> None:
        """Generates valid HTML with classic style."""
        generator = HTMLGenerator()
        html = generator.generate(sample_resume, style="classic")

        assert html
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html
        assert "Alice Johnson" in html
        assert "Product Manager" in html

    def test_generate_html_modern(self, sample_resume: Resume) -> None:
        """Generates valid HTML with modern style."""
        generator = HTMLGenerator()
        html = generator.generate(sample_resume, style="modern")

        assert html
        assert "Alice Johnson" in html

    def test_generate_html_tech(self, sample_resume: Resume) -> None:
        """Generates valid HTML with tech style."""
        generator = HTMLGenerator()
        html = generator.generate(sample_resume, style="tech")

        assert html
        assert "Alice Johnson" in html

    def test_generate_html_ats(self, sample_resume: Resume) -> None:
        """Generates valid HTML with ATS style."""
        generator = HTMLGenerator()
        html = generator.generate(sample_resume, style="ats")

        assert html
        assert "Alice Johnson" in html

    def test_generate_html_unknown_style_raises(self, sample_resume: Resume) -> None:
        """Unknown style raises ValueError."""
        generator = HTMLGenerator()

        with pytest.raises(ValueError, match="Unknown style"):
            generator.generate(sample_resume, style="unknown")

    def test_generated_html_has_semantic_structure(self, sample_resume: Resume) -> None:
        """Generated HTML has semantic structure."""
        generator = HTMLGenerator()
        html = generator.generate(sample_resume, style="classic")

        assert "<header" in html or 'role="banner"' in html
        assert "<main" in html or 'role="main"' in html

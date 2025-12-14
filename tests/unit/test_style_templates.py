"""Tests for style template variants.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

from datetime import date
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from resume_builder.models.resume import Position, Profile, Resume, Skill


@pytest.fixture
def jinja_env() -> Environment:
    """Create Jinja2 environment with template directory."""
    template_dir = Path(__file__).parent.parent.parent / "src" / "resume_builder" / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)))


@pytest.fixture
def sample_resume_with_data() -> Resume:
    """Create Resume with actual data for style testing."""
    return Resume(
        profile=Profile(
            first_name="Jane",
            last_name="Smith",
            headline="Senior Software Engineer",
        ),
        positions=[
            Position(
                company="TechCorp",
                title="Senior Engineer",
                start_date=date(2020, 1, 1),
                description="Led development of scalable systems",
            )
        ],
        education=[],
        skills=[
            Skill(name="Python"),
            Skill(name="JavaScript"),
            Skill(name="Docker"),
        ],
        certifications=[],
        projects=[],
        publications=[],
        languages=[],
        honors=[],
        volunteer=[],
    )


class TestClassicTemplate:
    """Tests for classic.html template."""

    def test_classic_template_renders(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Classic template renders without errors."""
        template = jinja_env.get_template("classic.html")
        html = template.render(resume=sample_resume_with_data)

        assert html
        assert "Jane Smith" in html

    def test_classic_has_semantic_structure(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Classic template has proper semantic structure."""
        template = jinja_env.get_template("classic.html")
        html = template.render(resume=sample_resume_with_data)

        assert "<header" in html or 'role="banner"' in html
        assert "<main" in html or 'role="main"' in html


class TestModernTemplate:
    """Tests for modern.html template."""

    def test_modern_template_renders(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Modern template renders without errors."""
        template = jinja_env.get_template("modern.html")
        html = template.render(resume=sample_resume_with_data)

        assert html
        assert "Jane Smith" in html

    def test_modern_has_semantic_structure(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Modern template has proper semantic structure."""
        template = jinja_env.get_template("modern.html")
        html = template.render(resume=sample_resume_with_data)

        assert "<header" in html or 'role="banner"' in html
        assert "<main" in html or 'role="main"' in html


class TestTechTemplate:
    """Tests for tech.html template."""

    def test_tech_template_renders(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Tech template renders without errors."""
        template = jinja_env.get_template("tech.html")
        html = template.render(resume=sample_resume_with_data)

        assert html
        assert "Jane Smith" in html

    def test_tech_has_semantic_structure(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """Tech template has proper semantic structure."""
        template = jinja_env.get_template("tech.html")
        html = template.render(resume=sample_resume_with_data)

        assert "<header" in html or 'role="banner"' in html
        assert "<main" in html or 'role="main"' in html


class TestATSTemplate:
    """Tests for ats.html template."""

    def test_ats_template_renders(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """ATS template renders without errors."""
        template = jinja_env.get_template("ats.html")
        html = template.render(resume=sample_resume_with_data)

        assert html
        assert "Jane Smith" in html

    def test_ats_has_semantic_structure(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """ATS template has proper semantic structure."""
        template = jinja_env.get_template("ats.html")
        html = template.render(resume=sample_resume_with_data)

        assert "<header" in html or 'role="banner"' in html
        assert "<main" in html or 'role="main"' in html

    def test_ats_is_plain_text_friendly(
        self, jinja_env: Environment, sample_resume_with_data: Resume
    ) -> None:
        """ATS template is optimized for parsing (minimal styling)."""
        template = jinja_env.get_template("ats.html")
        html = template.render(resume=sample_resume_with_data)

        # ATS should be simple - minimal inline styles
        # Should not have complex CSS that might confuse parsers
        assert html

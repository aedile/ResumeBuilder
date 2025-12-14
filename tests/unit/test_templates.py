"""Tests for HTML templates.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from resume_builder.models.resume import Profile, Resume


@pytest.fixture
def jinja_env() -> Environment:
    """Create Jinja2 environment with template directory."""
    template_dir = (
        Path(__file__).parent.parent.parent
        / "src"
        / "resume_builder"
        / "templates"
    )
    return Environment(loader=FileSystemLoader(str(template_dir)))


@pytest.fixture
def sample_resume() -> Resume:
    """Create minimal Resume for template testing."""
    return Resume(
        profile=Profile(
            first_name="John",
            last_name="Doe",
            headline="Software Engineer",
        ),
        positions=[],
        education=[],
        skills=[],
        certifications=[],
        projects=[],
        publications=[],
        languages=[],
        honors=[],
        volunteer=[],
    )


class TestBaseTemplate:
    """Tests for base HTML template."""

    def test_base_template_renders(
        self, jinja_env: Environment, sample_resume: Resume
    ) -> None:
        """Base template renders without Jinja errors."""
        template = jinja_env.get_template("base.html")
        html = template.render(resume=sample_resume)

        assert html
        assert "John Doe" in html
        assert "Software Engineer" in html

    def test_template_has_proper_heading_hierarchy(
        self, jinja_env: Environment, sample_resume: Resume
    ) -> None:
        """Template has h1 for name, h2 for sections."""
        template = jinja_env.get_template("base.html")
        html = template.render(resume=sample_resume)

        # h1 should contain full name
        assert "<h1" in html
        assert "John Doe" in html

        # Should have h2 for main sections
        assert "<h2" in html

    def test_template_has_aria_landmarks(
        self, jinja_env: Environment, sample_resume: Resume
    ) -> None:
        """Template includes ARIA landmark roles."""
        template = jinja_env.get_template("base.html")
        html = template.render(resume=sample_resume)

        # Main content area
        assert 'role="main"' in html or "<main" in html

        # Header with contact info
        assert 'role="banner"' in html or "<header" in html

    def test_template_has_print_styles(
        self, jinja_env: Environment, sample_resume: Resume
    ) -> None:
        """Template includes print media query styles."""
        template = jinja_env.get_template("base.html")
        html = template.render(resume=sample_resume)

        # Should reference print styles
        assert "@media print" in html or 'media="print"' in html

    def test_template_has_semantic_html(
        self, jinja_env: Environment, sample_resume: Resume
    ) -> None:
        """Template uses semantic HTML5 elements."""
        template = jinja_env.get_template("base.html")
        html = template.render(resume=sample_resume)

        # Should use semantic elements
        assert "<section" in html or "<article" in html
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html

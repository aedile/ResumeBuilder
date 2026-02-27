"""Tests for HTML generator and generator constants.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

from datetime import date

import pytest

from resume_builder.generators import SUPPORTED_STYLES
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
                title="Senior PM",
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
        html = HTMLGenerator().generate(sample_resume, style="modern")

        assert html
        assert "Alice Johnson" in html

    def test_generate_html_tech(self, sample_resume: Resume) -> None:
        """Generates valid HTML with tech style."""
        html = HTMLGenerator().generate(sample_resume, style="tech")

        assert html
        assert "Alice Johnson" in html

    def test_generate_html_ats(self, sample_resume: Resume) -> None:
        """Generates valid HTML with ATS style."""
        html = HTMLGenerator().generate(sample_resume, style="ats")

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


class TestHTMLGeneratorContentRendering:
    """HTMLGenerator renders all resume content faithfully and safely."""

    def test_renders_position_company_name(self, sample_resume: Resume) -> None:
        """Position company name appears in the rendered HTML output."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "StartupCo" in html

    def test_renders_position_title(self, sample_resume: Resume) -> None:
        """Position title (distinct from profile headline) appears in output."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "Senior PM" in html

    def test_renders_position_date_range(self, sample_resume: Resume) -> None:
        """Position start month/year and 'Present' appear for a current position."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "March 2021" in html
        assert "Present" in html

    def test_renders_skill_names(self, sample_resume: Resume) -> None:
        """All skill names appear in the rendered HTML output."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "Product Management" in html
        assert "Agile" in html

    def test_renders_section_headings(self, sample_resume: Resume) -> None:
        """Experience and Skills section headings appear when data is present."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "Professional Experience" in html
        assert "Skills" in html

    def test_escapes_html_in_user_content(self) -> None:
        """HTML in user-supplied fields is escaped to prevent XSS injection."""
        resume = Resume(
            profile=Profile(
                first_name="<script>alert('xss')</script>",
                last_name="Test",
                headline="Engineer",
            ),
        )
        html = HTMLGenerator().generate(resume, style="classic")

        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_empty_positions_section_omitted(self) -> None:
        """Professional Experience section is absent when the resume has no positions."""
        resume = Resume(
            profile=Profile(first_name="Jane", last_name="Smith", headline="Designer"),
        )
        html = HTMLGenerator().generate(resume, style="classic")
        assert "Professional Experience" not in html

    def test_empty_skills_section_omitted(self) -> None:
        """Skills section is absent when the resume has no skills."""
        resume = Resume(
            profile=Profile(first_name="Jane", last_name="Smith", headline="Designer"),
        )
        html = HTMLGenerator().generate(resume, style="classic")
        assert "Skills" not in html

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_all_styles_render_company_name(
        self, sample_resume: Resume, style: str
    ) -> None:
        """Company name is present in output for every supported style."""
        html = HTMLGenerator().generate(sample_resume, style=style)
        assert "StartupCo" in html, f"Company name missing in {style!r} style"

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_all_styles_render_skills(self, sample_resume: Resume, style: str) -> None:
        """Skill names are present in output for every supported style."""
        html = HTMLGenerator().generate(sample_resume, style=style)
        assert "Product Management" in html, f"Skill 'Product Management' missing in {style!r}"
        assert "Agile" in html, f"Skill 'Agile' missing in {style!r}"

    def test_position_description_rendered(self, sample_resume: Resume) -> None:
        """Position description text appears in the rendered output."""
        html = HTMLGenerator().generate(sample_resume, style="classic")
        assert "Led product development" in html


class TestGeneratorConstants:
    """Tests for the shared generator constants module."""

    def test_supported_styles_importable_from_generators_package(self) -> None:
        """SUPPORTED_STYLES is importable directly from resume_builder.generators."""
        from resume_builder.generators import SUPPORTED_STYLES  # noqa: PLC0415

        assert isinstance(SUPPORTED_STYLES, list)
        assert len(SUPPORTED_STYLES) > 0

    def test_supported_styles_contains_expected_values(self) -> None:
        """SUPPORTED_STYLES contains exactly the four expected style names."""
        from resume_builder.generators import SUPPORTED_STYLES  # noqa: PLC0415

        assert set(SUPPORTED_STYLES) == {"classic", "modern", "tech", "ats"}

    def test_supported_styles_importable_from_constants_module(self) -> None:
        """SUPPORTED_STYLES is importable from the constants submodule directly."""
        from resume_builder.generators.constants import SUPPORTED_STYLES  # noqa: PLC0415

        assert isinstance(SUPPORTED_STYLES, list)

    def test_html_generator_uses_shared_supported_styles(self) -> None:
        """HTMLGenerator validates styles against the shared SUPPORTED_STYLES list."""
        from resume_builder.generators import SUPPORTED_STYLES  # noqa: PLC0415
        from resume_builder.generators.html import SUPPORTED_STYLES as HTML_STYLES  # noqa: PLC0415

        assert SUPPORTED_STYLES is HTML_STYLES

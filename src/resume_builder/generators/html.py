"""HTML generator for resumes.

CONSTITUTION Priority 5: Type hints, docstrings
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from resume_builder.models.resume import Resume

# Supported styles
SUPPORTED_STYLES = ["classic", "modern", "tech", "ats"]


class HTMLGenerator:
    """Generate HTML resumes from Resume objects using Jinja2 templates."""

    def __init__(self) -> None:
        """Initialize HTMLGenerator with template environment."""
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,  # Prevent XSS
        )

    def generate(self, resume: Resume, style: str = "classic") -> str:
        """Generate HTML resume with specified style.

        Args:
            resume: Resume object to render.
            style: Style template to use (classic, modern, tech, ats).

        Returns:
            Rendered HTML string.

        Raises:
            ValueError: If style is not supported.

        """
        if style not in SUPPORTED_STYLES:
            raise ValueError(
                f"Unknown style: {style}. Supported styles: {', '.join(SUPPORTED_STYLES)}"
            )

        template_name = f"{style}.html"

        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as e:
            raise ValueError(f"Template not found for style: {style}") from e

        return template.render(resume=resume)

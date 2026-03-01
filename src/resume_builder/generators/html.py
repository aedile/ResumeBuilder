"""HTML generator for resumes.

CONSTITUTION Priority 5: Type hints, docstrings
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility
"""

import importlib.resources

from jinja2 import Environment, FileSystemLoader

from resume_builder.generators.constants import SUPPORTED_STYLES
from resume_builder.models.resume import Resume


class HTMLGenerator:
    """Generate HTML resumes from Resume objects using Jinja2 templates."""

    def __init__(self) -> None:
        """Initialize HTMLGenerator with template environment."""
        template_dir = importlib.resources.files("resume_builder") / "templates"
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
                f"Unknown style: {style}. Supported styles: {', '.join(sorted(SUPPORTED_STYLES))}"
            )

        template_name = f"{style}.html"
        template = self.env.get_template(template_name)
        return template.render(resume=resume)

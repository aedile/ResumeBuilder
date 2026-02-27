"""PDF generator for resumes using WeasyPrint.

CONSTITUTION Priority 5: Type hints, docstrings
CONSTITUTION Priority 9: WCAG 2.1 AA Accessibility (inherited from HTML templates)
"""

from typing import cast

from weasyprint import HTML

from resume_builder.generators.constants import SUPPORTED_STYLES
from resume_builder.generators.html import HTMLGenerator
from resume_builder.models.resume import Resume


class PDFGenerator:
    """Generate PDF resumes from Resume objects using WeasyPrint.

    Converts the HTML output of HTMLGenerator to PDF, so all visual
    styles and accessibility features from the HTML templates are
    preserved in the PDF output.
    """

    def __init__(self) -> None:
        """Initialize PDFGenerator with an embedded HTML generator."""
        self.html_generator = HTMLGenerator()

    def generate(self, resume: Resume, style: str = "classic") -> bytes:
        """Generate a PDF resume with the specified style.

        Args:
            resume: Resume object to render.
            style: Visual style to use (classic, modern, tech, ats).

        Returns:
            PDF document as raw bytes.

        Raises:
            ValueError: If style is not in SUPPORTED_STYLES.

        """
        if style not in SUPPORTED_STYLES:
            raise ValueError(
                f"Unknown style: {style}. Supported styles: {', '.join(SUPPORTED_STYLES)}"
            )

        html_content = self.html_generator.generate(resume, style=style)
        # cast: weasyprint has no type stubs; write_pdf() returns bytes at runtime
        return cast("bytes", HTML(string=html_content).write_pdf())

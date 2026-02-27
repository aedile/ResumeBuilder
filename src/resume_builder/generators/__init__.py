"""Resume generators for HTML, PDF, and DOCX."""

from resume_builder.generators.constants import SUPPORTED_STYLES
from resume_builder.generators.html import HTMLGenerator

__all__ = ["SUPPORTED_STYLES", "HTMLGenerator"]

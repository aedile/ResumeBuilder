"""Resume Builder - A professional resume generator from LinkedIn data exports.

This package provides tools to parse LinkedIn data exports and generate
polished, customizable resumes in multiple formats (HTML, PDF, DOCX).
"""

from resume_builder.exceptions import (
    ExportNotFoundError,
    InvalidExportError,
    ParseError,
    ResumeBuilderError,
)

__version__ = "0.1.0"
__author__ = "Resume Builder Contributors"
__all__ = [
    "ExportNotFoundError",
    "InvalidExportError",
    "ParseError",
    "ResumeBuilderError",
]

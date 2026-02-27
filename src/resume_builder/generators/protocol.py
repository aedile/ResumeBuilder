"""Structural protocol shared by all resume generators.

CONSTITUTION Priority 5: Type hints, docstrings
"""

from typing import Protocol, runtime_checkable

from resume_builder.models.resume import Resume


@runtime_checkable
class GeneratorProtocol(Protocol):
    """Interface that every resume generator must satisfy.

    Both PDFGenerator and DOCXGenerator implement this protocol so that
    callers can treat them interchangeably (e.g. for batch export).
    """

    def generate(self, resume: Resume, style: str = "classic") -> bytes:
        """Generate a resume document and return the raw bytes.

        Args:
            resume: Resume object to render.
            style: Visual style to use (classic, modern, tech, ats).

        Returns:
            Raw document bytes (PDF or DOCX depending on implementation).

        Raises:
            ValueError: If style is not in SUPPORTED_STYLES.

        """
        ...

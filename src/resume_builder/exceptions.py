"""Domain exception types for Resume Builder.

All exceptions raised by parsers and generators inherit from
ResumeBuilderError so callers can catch the full hierarchy with a
single except clause when needed.
"""


class ResumeBuilderError(Exception):
    """Base exception for all Resume Builder errors."""


class ExportNotFoundError(ResumeBuilderError):
    """Raised when the LinkedIn export directory does not exist."""


class InvalidExportError(ResumeBuilderError):
    """Raised when the export directory is present but structurally invalid.

    Examples:
        - Profile.csv is missing (required file)
        - Export is not a directory and ZIP support is not implemented
    """


class ParseError(ResumeBuilderError):
    """Raised when a CSV file cannot be parsed into a model.

    Examples:
        - Required file is not found
        - CSV is empty or has no data rows
        - Required column headers are absent
    """

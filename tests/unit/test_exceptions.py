"""Tests for domain exception types.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
"""

import pytest


class TestExceptionHierarchy:
    """Domain exceptions inherit from ResumeBuilderError base."""

    def test_resume_builder_error_importable(self) -> None:
        """ResumeBuilderError is importable from resume_builder.exceptions."""
        from resume_builder.exceptions import ResumeBuilderError  # noqa: PLC0415

        assert issubclass(ResumeBuilderError, Exception)

    def test_export_not_found_error_importable(self) -> None:
        """ExportNotFoundError is importable from resume_builder.exceptions."""
        from resume_builder.exceptions import ExportNotFoundError  # noqa: PLC0415

        assert issubclass(ExportNotFoundError, Exception)

    def test_invalid_export_error_importable(self) -> None:
        """InvalidExportError is importable from resume_builder.exceptions."""
        from resume_builder.exceptions import InvalidExportError  # noqa: PLC0415

        assert issubclass(InvalidExportError, Exception)

    def test_parse_error_importable(self) -> None:
        """ParseError is importable from resume_builder.exceptions."""
        from resume_builder.exceptions import ParseError  # noqa: PLC0415

        assert issubclass(ParseError, Exception)

    def test_export_not_found_inherits_from_base(self) -> None:
        """ExportNotFoundError is a subclass of ResumeBuilderError."""
        from resume_builder.exceptions import (  # noqa: PLC0415
            ExportNotFoundError,
            ResumeBuilderError,
        )

        assert issubclass(ExportNotFoundError, ResumeBuilderError)

    def test_invalid_export_inherits_from_base(self) -> None:
        """InvalidExportError is a subclass of ResumeBuilderError."""
        from resume_builder.exceptions import (  # noqa: PLC0415
            InvalidExportError,
            ResumeBuilderError,
        )

        assert issubclass(InvalidExportError, ResumeBuilderError)

    def test_parse_error_inherits_from_base(self) -> None:
        """ParseError is a subclass of ResumeBuilderError."""
        from resume_builder.exceptions import ParseError, ResumeBuilderError  # noqa: PLC0415

        assert issubclass(ParseError, ResumeBuilderError)


class TestExceptionInstantiation:
    """Domain exceptions carry meaningful messages."""

    def test_resume_builder_error_carries_message(self) -> None:
        """ResumeBuilderError preserves its message."""
        from resume_builder.exceptions import ResumeBuilderError  # noqa: PLC0415

        exc = ResumeBuilderError("something went wrong")
        assert "something went wrong" in str(exc)

    def test_export_not_found_error_carries_message(self) -> None:
        """ExportNotFoundError preserves its message."""
        from resume_builder.exceptions import ExportNotFoundError  # noqa: PLC0415

        exc = ExportNotFoundError("Directory not found: /tmp/missing")
        assert "Directory not found" in str(exc)

    def test_invalid_export_error_carries_message(self) -> None:
        """InvalidExportError preserves its message."""
        from resume_builder.exceptions import InvalidExportError  # noqa: PLC0415

        exc = InvalidExportError("Profile.csv is required")
        assert "Profile.csv" in str(exc)

    def test_parse_error_carries_message(self) -> None:
        """ParseError preserves its message."""
        from resume_builder.exceptions import ParseError  # noqa: PLC0415

        exc = ParseError("Missing required fields: Title")
        assert "Missing required fields" in str(exc)


class TestTopLevelImports:
    """Domain exceptions are accessible from the top-level package."""

    def test_resume_builder_error_importable_from_package(self) -> None:
        """ResumeBuilderError importable from resume_builder."""
        from resume_builder import ResumeBuilderError  # noqa: PLC0415

        assert issubclass(ResumeBuilderError, Exception)

    def test_export_not_found_importable_from_package(self) -> None:
        """ExportNotFoundError importable from resume_builder."""
        from resume_builder import ExportNotFoundError  # noqa: PLC0415

        assert issubclass(ExportNotFoundError, Exception)

    def test_invalid_export_importable_from_package(self) -> None:
        """InvalidExportError importable from resume_builder."""
        from resume_builder import InvalidExportError  # noqa: PLC0415

        assert issubclass(InvalidExportError, Exception)

    def test_parse_error_importable_from_package(self) -> None:
        """ParseError importable from resume_builder."""
        from resume_builder import ParseError  # noqa: PLC0415

        assert issubclass(ParseError, Exception)


class TestExceptionCatchability:
    """All domain exceptions are catchable by their parent types."""

    def test_export_not_found_catchable_as_base(self) -> None:
        """ExportNotFoundError instance is caught by ResumeBuilderError handler."""
        from resume_builder.exceptions import (  # noqa: PLC0415
            ExportNotFoundError,
            ResumeBuilderError,
        )

        with pytest.raises(ResumeBuilderError):
            raise ExportNotFoundError("test")

    def test_invalid_export_catchable_as_base(self) -> None:
        """InvalidExportError instance is caught by ResumeBuilderError handler."""
        from resume_builder.exceptions import (  # noqa: PLC0415
            InvalidExportError,
            ResumeBuilderError,
        )

        with pytest.raises(ResumeBuilderError):
            raise InvalidExportError("test")

    def test_parse_error_catchable_as_base(self) -> None:
        """ParseError instance is caught by ResumeBuilderError handler."""
        from resume_builder.exceptions import ParseError, ResumeBuilderError  # noqa: PLC0415

        with pytest.raises(ResumeBuilderError):
            raise ParseError("test")

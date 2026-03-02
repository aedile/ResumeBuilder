"""Tests for QA and HR review agent tools.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage
All tools are pure functions — no Claude API calls.
"""

from __future__ import annotations

import json

import pytest

from resume_builder.agents.tools.review import (
    CHECK_ACCESSIBILITY_TOOL,
    CHECK_PRINT_QUALITY_TOOL,
    EVALUATE_LAYOUT_TOOL,
    VERIFY_CONTRAST_TOOL,
    check_accessibility,
    check_print_quality,
    evaluate_layout,
    verify_contrast,
)
from resume_builder.models.agent import ToolDefinition

# ---------------------------------------------------------------------------
# check_accessibility
# ---------------------------------------------------------------------------


class TestCheckAccessibility:
    """Tests for check_accessibility tool function."""

    def test_valid_heading_hierarchy_passes(self) -> None:
        """check_accessibility accepts sequential heading levels h1→h2→h3."""
        html = (
            "<html><body><main><h1>Name</h1><h2>Experience</h2><h3>Role</h3></main></body></html>"
        )
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert data["is_accessible"] is True

    def test_skipped_heading_level_is_flagged(self) -> None:
        """check_accessibility flags heading that skips a level (h1 → h3)."""
        html = "<html><body><h1>Name</h1><h3>Role</h3></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert data["is_accessible"] is False
        assert any("heading" in issue.lower() for issue in data["issues"])

    def test_missing_alt_text_is_flagged(self) -> None:
        """check_accessibility flags img elements missing alt attribute."""
        html = "<html><body><h1>Name</h1><img src='photo.jpg'/></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert any("alt" in issue.lower() for issue in data["issues"])

    def test_image_with_alt_text_passes(self) -> None:
        """check_accessibility accepts img elements with alt attribute."""
        html = "<html><body><h1>Name</h1><img src='photo.jpg' alt='Profile photo'/></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        # No alt-text issues expected
        assert not any("alt" in issue.lower() for issue in data["issues"])

    def test_missing_main_landmark_is_flagged(self) -> None:
        """check_accessibility flags HTML lacking a <main> landmark element."""
        html = "<html><body><div><h1>Name</h1></div></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert any(
            "main" in issue.lower() or "landmark" in issue.lower() for issue in data["issues"]
        )

    def test_document_with_main_landmark_passes(self) -> None:
        """check_accessibility accepts HTML with a <main> landmark."""
        html = "<html><body><main><h1>Name</h1><h2>Experience</h2></main></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert not any(
            "main" in issue.lower() or "landmark" in issue.lower() for issue in data["issues"]
        )

    def test_role_main_accepted_as_landmark(self) -> None:
        """check_accessibility accepts role='main' as equivalent to <main> element."""
        html = '<html><body><div role="main"><h1>Name</h1><h2>Section</h2></div></body></html>'
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert not any(
            "main" in issue.lower() or "landmark" in issue.lower() for issue in data["issues"]
        )

    def test_returns_json_string(self) -> None:
        """check_accessibility always returns a valid JSON string."""
        result = check_accessibility(html_content="<html><body><h1>Test</h1></body></html>")
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "is_accessible" in data
        assert "issues" in data

    def test_empty_html_returns_issues(self) -> None:
        """check_accessibility returns issues for empty HTML content."""
        result = check_accessibility(html_content="")
        data = json.loads(result)
        assert isinstance(data["issues"], list)

    def test_issues_is_list_of_strings(self) -> None:
        """check_accessibility issues field is always a list of strings."""
        html = "<html><body><h1>Test</h1></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert isinstance(data["issues"], list)
        for issue in data["issues"]:
            assert isinstance(issue, str)

    def test_multiple_h1_is_flagged(self) -> None:
        """check_accessibility flags documents with more than one h1."""
        html = "<html><body><h1>Name</h1><h1>Another H1</h1></body></html>"
        result = check_accessibility(html_content=html)
        data = json.loads(result)
        assert any("h1" in issue.lower() for issue in data["issues"])


# ---------------------------------------------------------------------------
# evaluate_layout
# ---------------------------------------------------------------------------


class TestEvaluateLayout:
    """Tests for evaluate_layout tool function."""

    def test_well_structured_resume_scores_high(self) -> None:
        """evaluate_layout returns a high score for a well-structured resume."""
        html = (
            "<html><body><main>"
            "<header><h1>Alex Chen</h1></header>"
            "<section><h2>Experience</h2><p>Engineer at Acme</p></section>"
            "<section><h2>Education</h2><p>BS Computer Science</p></section>"
            "<section><h2>Skills</h2><p>Python, SQL</p></section>"
            "</main></body></html>"
        )
        result = evaluate_layout(html_content=html)
        data = json.loads(result)
        assert data["layout_score"] >= 60

    def test_missing_experience_section_reduces_score(self) -> None:
        """evaluate_layout penalises HTML without an experience section."""
        html = "<html><body><main><h1>Alex Chen</h1></main></body></html>"
        result = evaluate_layout(html_content=html)
        data = json.loads(result)
        assert data["layout_score"] == 20  # 20pts for h1 only; no sections, no header

    def test_returns_sections_found_list(self) -> None:
        """evaluate_layout returns a list of identified section names."""
        html = (
            "<html><body><main>"
            "<h1>Name</h1>"
            "<h2>Experience</h2>"
            "<h2>Education</h2>"
            "</main></body></html>"
        )
        result = evaluate_layout(html_content=html)
        data = json.loads(result)
        assert isinstance(data["sections_found"], list)

    def test_returns_suggestions_list(self) -> None:
        """evaluate_layout always returns a suggestions list."""
        result = evaluate_layout(html_content="<html><body><h1>Name</h1></body></html>")
        data = json.loads(result)
        assert isinstance(data["suggestions"], list)

    def test_returns_json_string(self) -> None:
        """evaluate_layout always returns a valid JSON string."""
        result = evaluate_layout(html_content="<html><body></body></html>")
        data = json.loads(result)
        assert "layout_score" in data
        assert "sections_found" in data
        assert "suggestions" in data

    def test_layout_score_is_integer_0_to_100(self) -> None:
        """evaluate_layout returns an integer score between 0 and 100."""
        result = evaluate_layout(html_content="<html><body><h1>Test</h1></body></html>")
        data = json.loads(result)
        assert isinstance(data["layout_score"], int)
        assert 0 <= data["layout_score"] <= 100

    def test_empty_html_returns_zero_score(self) -> None:
        """evaluate_layout returns score of 0 for empty HTML."""
        result = evaluate_layout(html_content="")
        data = json.loads(result)
        assert data["layout_score"] == 0

    def test_suggestions_are_strings(self) -> None:
        """evaluate_layout suggestions are strings."""
        html = "<html><body><h1>Name</h1></body></html>"
        result = evaluate_layout(html_content=html)
        data = json.loads(result)
        for suggestion in data["suggestions"]:
            assert isinstance(suggestion, str)


# ---------------------------------------------------------------------------
# verify_contrast
# ---------------------------------------------------------------------------


class TestVerifyContrast:
    """Tests for verify_contrast tool function."""

    def test_black_on_white_passes_aa_normal(self) -> None:
        """verify_contrast: black (#000000) on white (#ffffff) has ratio 21:1 → passes."""
        result = verify_contrast(foreground="#000000", background="#ffffff")
        data = json.loads(result)
        assert data["passes_aa_normal"] is True
        assert data["ratio"] >= 21.0

    def test_white_on_white_fails_aa_normal(self) -> None:
        """verify_contrast: white on white has ratio 1:1 → fails."""
        result = verify_contrast(foreground="#ffffff", background="#ffffff")
        data = json.loads(result)
        assert data["passes_aa_normal"] is False
        assert abs(data["ratio"] - 1.0) < 0.01

    def test_low_contrast_fails(self) -> None:
        """verify_contrast: light grey on white fails AA normal (ratio < 4.5)."""
        # #aaaaaa on #ffffff ≈ 2.32:1
        result = verify_contrast(foreground="#aaaaaa", background="#ffffff")
        data = json.loads(result)
        assert data["passes_aa_normal"] is False

    def test_passes_large_text_threshold(self) -> None:
        """verify_contrast: ratio ≥ 3:1 passes AA large text even if < 4.5:1."""
        # #767676 on #ffffff ≈ 4.54:1 passes both; use a value that passes large but not normal
        # #949494 on #ffffff ≈ 2.85:1 — fails both
        # #969696 on #ffffff ≈ 2.97:1 — fails normal; we need something ~3.1-4.4:1
        # #757575 on #ffffff ≈ 4.48:1 — very close to normal threshold
        # Let's use #888888 on #ffffff ≈ 3.54:1 → passes large, fails normal
        result = verify_contrast(foreground="#888888", background="#ffffff")
        data = json.loads(result)
        assert data["passes_aa_large"] is True
        assert data["passes_aa_normal"] is False

    def test_ratio_is_float(self) -> None:
        """verify_contrast returns ratio as a float."""
        result = verify_contrast(foreground="#000000", background="#ffffff")
        data = json.loads(result)
        assert isinstance(data["ratio"], float)

    def test_returns_json_string(self) -> None:
        """verify_contrast always returns a valid JSON string."""
        result = verify_contrast(foreground="#000000", background="#ffffff")
        data = json.loads(result)
        assert "ratio" in data
        assert "passes_aa_normal" in data
        assert "passes_aa_large" in data

    def test_symmetric_colors(self) -> None:
        """verify_contrast gives same ratio regardless of foreground/background order."""
        result_a = verify_contrast(foreground="#000000", background="#ffffff")
        result_b = verify_contrast(foreground="#ffffff", background="#000000")
        data_a = json.loads(result_a)
        data_b = json.loads(result_b)
        assert abs(data_a["ratio"] - data_b["ratio"]) < 0.01

    def test_invalid_color_returns_error(self) -> None:
        """verify_contrast returns error JSON for invalid hex color strings."""
        result = verify_contrast(foreground="not-a-color", background="#ffffff")
        data = json.loads(result)
        assert "error" in data

    def test_three_digit_hex_accepted(self) -> None:
        """verify_contrast accepts 3-digit hex shorthand (#fff, #000)."""
        result = verify_contrast(foreground="#000", background="#fff")
        data = json.loads(result)
        assert "ratio" in data
        assert "error" not in data


# ---------------------------------------------------------------------------
# check_print_quality
# ---------------------------------------------------------------------------


class TestCheckPrintQuality:
    """Tests for check_print_quality tool function."""

    def test_clean_html_is_print_ready(self) -> None:
        """check_print_quality: simple semantic HTML is print-ready."""
        html = (
            "<html><body><main>"
            "<h1>Alex Chen</h1>"
            "<h2>Experience</h2><p>Engineer at Acme</p>"
            "</main></body></html>"
        )
        result = check_print_quality(html_content=html)
        data = json.loads(result)
        assert data["print_ready"] is True

    def test_display_none_is_flagged(self) -> None:
        """check_print_quality flags elements with display:none inline style."""
        html = (
            "<html><body><h1>Name</h1><section style='display:none'>Hidden</section></body></html>"
        )
        result = check_print_quality(html_content=html)
        data = json.loads(result)
        assert any(
            "display" in issue.lower() or "hidden" in issue.lower() for issue in data["issues"]
        )

    def test_overflow_hidden_is_flagged(self) -> None:
        """check_print_quality flags elements with overflow:hidden that could clip content."""
        html = (
            "<html><body>"
            "<div style='overflow:hidden;height:100px'><h1>Name</h1><p>Long content...</p></div>"
            "</body></html>"
        )
        result = check_print_quality(html_content=html)
        data = json.loads(result)
        assert any(
            "overflow" in issue.lower() or "clip" in issue.lower() for issue in data["issues"]
        )

    def test_returns_issues_list(self) -> None:
        """check_print_quality always returns an issues list."""
        result = check_print_quality(html_content="<html><body></body></html>")
        data = json.loads(result)
        assert isinstance(data["issues"], list)

    def test_returns_json_string(self) -> None:
        """check_print_quality always returns a valid JSON string."""
        result = check_print_quality(html_content="<html><body><h1>Test</h1></body></html>")
        data = json.loads(result)
        assert "print_ready" in data
        assert "issues" in data

    def test_empty_html_is_not_print_ready(self) -> None:
        """check_print_quality marks empty HTML as not print-ready."""
        result = check_print_quality(html_content="")
        data = json.loads(result)
        assert data["print_ready"] is False

    def test_issues_are_strings(self) -> None:
        """check_print_quality issues are strings."""
        html = "<html><body><div style='display:none'>x</div></body></html>"
        result = check_print_quality(html_content=html)
        data = json.loads(result)
        for issue in data["issues"]:
            assert isinstance(issue, str)

    def test_fixed_height_with_overflow_is_flagged(self) -> None:
        """check_print_quality flags fixed-height containers that may clip content."""
        html = (
            "<html><body>"
            "<div style='height:200px;overflow:hidden'><p>Content</p></div>"
            "</body></html>"
        )
        result = check_print_quality(html_content=html)
        data = json.loads(result)
        assert len(data["issues"]) > 0


# ---------------------------------------------------------------------------
# ToolDefinition schemas
# ---------------------------------------------------------------------------


class TestReviewToolDefinitions:
    """Tests for ToolDefinition schemas exported from review module."""

    @pytest.mark.parametrize(
        "tool",
        [
            CHECK_ACCESSIBILITY_TOOL,
            EVALUATE_LAYOUT_TOOL,
            VERIFY_CONTRAST_TOOL,
            CHECK_PRINT_QUALITY_TOOL,
        ],
    )
    def test_tool_is_tool_definition(self, tool: ToolDefinition) -> None:
        """Each exported tool constant is a ToolDefinition instance."""
        assert isinstance(tool, ToolDefinition)

    @pytest.mark.parametrize(
        "tool",
        [
            CHECK_ACCESSIBILITY_TOOL,
            EVALUATE_LAYOUT_TOOL,
            VERIFY_CONTRAST_TOOL,
            CHECK_PRINT_QUALITY_TOOL,
        ],
    )
    def test_tool_has_non_empty_name(self, tool: ToolDefinition) -> None:
        """Each tool definition has a non-empty name."""
        assert tool.name

    @pytest.mark.parametrize(
        "tool",
        [
            CHECK_ACCESSIBILITY_TOOL,
            EVALUATE_LAYOUT_TOOL,
            VERIFY_CONTRAST_TOOL,
            CHECK_PRINT_QUALITY_TOOL,
        ],
    )
    def test_tool_has_valid_input_schema(self, tool: ToolDefinition) -> None:
        """Each tool definition has a valid JSON Schema object."""
        schema = tool.input_schema
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema

    def test_check_accessibility_tool_name(self) -> None:
        """CHECK_ACCESSIBILITY_TOOL has the expected name."""
        assert CHECK_ACCESSIBILITY_TOOL.name == "check_accessibility"

    def test_evaluate_layout_tool_name(self) -> None:
        """EVALUATE_LAYOUT_TOOL has the expected name."""
        assert EVALUATE_LAYOUT_TOOL.name == "evaluate_layout"

    def test_verify_contrast_tool_name(self) -> None:
        """VERIFY_CONTRAST_TOOL has the expected name."""
        assert VERIFY_CONTRAST_TOOL.name == "verify_contrast"

    def test_check_print_quality_tool_name(self) -> None:
        """CHECK_PRINT_QUALITY_TOOL has the expected name."""
        assert CHECK_PRINT_QUALITY_TOOL.name == "check_print_quality"

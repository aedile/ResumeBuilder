"""QA and HR review agent tools.

These tools are registered with QAAgent and HRAgent and called by Claude
via tool_use to evaluate resume quality, accessibility, and professional
polish.

All functions accept and return strings (JSON-encoded where structured) to
conform to the Anthropic tool result format.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser

from resume_builder.models.agent import ToolDefinition

# ---------------------------------------------------------------------------
# Tool Definitions (JSON schemas forwarded to the Anthropic API)
# ---------------------------------------------------------------------------

CHECK_ACCESSIBILITY_TOOL = ToolDefinition(
    name="check_accessibility",
    description=(
        "Analyse HTML content for WCAG 2.1 AA accessibility issues. Checks heading "
        "hierarchy (no skipped levels, single h1), alt text on images, and presence "
        "of landmark elements. Returns a JSON object with is_accessible (bool) and "
        "issues (list of strings describing each violation found)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "html_content": {
                "type": "string",
                "description": "Full HTML content of the resume to analyse.",
            },
        },
        "required": ["html_content"],
    },
)

EVALUATE_LAYOUT_TOOL = ToolDefinition(
    name="evaluate_layout",
    description=(
        "Evaluate the visual hierarchy and section structure of HTML resume content. "
        "Returns a JSON object with layout_score (int 0-100), sections_found (list of "
        "section names detected), and suggestions (list of actionable improvement strings)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "html_content": {
                "type": "string",
                "description": "Full HTML content of the resume to evaluate.",
            },
        },
        "required": ["html_content"],
    },
)

VERIFY_CONTRAST_TOOL = ToolDefinition(
    name="verify_contrast",
    description=(
        "Calculate the WCAG contrast ratio between two hex colour values and check "
        "whether it meets AA thresholds. Returns a JSON object with ratio (float), "
        "passes_aa_normal (bool, threshold 4.5:1), and passes_aa_large (bool, threshold 3:1). "
        'On invalid colour input, returns {"error": "..."}.'
    ),
    input_schema={
        "type": "object",
        "properties": {
            "foreground": {
                "type": "string",
                "description": "Foreground (text) colour as hex, e.g. '#000000' or '#000'.",
            },
            "background": {
                "type": "string",
                "description": "Background colour as a hex string, e.g. '#ffffff' or '#fff'.",
            },
        },
        "required": ["foreground", "background"],
    },
)

CHECK_PRINT_QUALITY_TOOL = ToolDefinition(
    name="check_print_quality",
    description=(
        "Inspect HTML content for patterns that cause poor print rendering: elements "
        "with display:none, overflow:hidden with fixed heights, or other print-unfriendly "
        "inline styles. Returns a JSON object with print_ready (bool) and issues (list)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "html_content": {
                "type": "string",
                "description": "Full HTML content of the resume to inspect.",
            },
        },
        "required": ["html_content"],
    },
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_SECTION_KEYWORDS: dict[str, list[str]] = {
    "experience": ["experience", "work", "employment", "positions", "history"],
    "education": ["education", "academic", "degree", "university", "college"],
    "skills": ["skills", "technologies", "competencies", "expertise"],
    "summary": ["summary", "profile", "about", "objective"],
}

# ---------------------------------------------------------------------------
# Internal HTML parser helpers
# ---------------------------------------------------------------------------


class _HeadingAltParser(HTMLParser):
    """Collect heading levels, img alt attributes, and landmark tags from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.headings: list[int] = []
        self.img_missing_alt: int = 0
        self.has_main: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if re.fullmatch(r"h[1-6]", tag_lower):
            self.headings.append(int(tag_lower[1]))
        elif tag_lower == "img":
            attr_dict = dict(attrs)
            if "alt" not in attr_dict:
                self.img_missing_alt += 1
        elif tag_lower == "main":
            self.has_main = True
        else:
            attr_dict = dict(attrs)
            if attr_dict.get("role") == "main":
                self.has_main = True


class _SectionParser(HTMLParser):
    """Collect h2 text content and tag presence for layout evaluation."""

    def __init__(self) -> None:
        super().__init__()
        self.h2_texts: list[str] = []
        self.has_h1: bool = False
        self.has_header: bool = False
        self._in_heading: int = 0  # heading level currently open
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if re.fullmatch(r"h[1-6]", tag_lower):
            self._in_heading = int(tag_lower[1])
            self._current_text = []
        elif tag_lower == "header":
            self.has_header = True

    def handle_endtag(self, tag: str) -> None:
        if re.fullmatch(r"h[1-6]", tag.lower()):
            text = "".join(self._current_text).strip().lower()
            if self._in_heading == 1:
                self.has_h1 = True
            elif self._in_heading == 2:
                self.h2_texts.append(text)
            self._in_heading = 0

    def handle_data(self, data: str) -> None:
        if self._in_heading:
            self._current_text.append(data)


class _StyleParser(HTMLParser):
    """Collect inline style attributes for print-quality analysis."""

    def __init__(self) -> None:
        super().__init__()
        self.style_attrs: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        style = attr_dict.get("style")
        if style:
            self.style_attrs.append(style.lower())


# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------


def check_accessibility(html_content: str) -> str:
    """Analyse HTML for WCAG 2.1 AA accessibility issues.

    Checks:
    - Heading hierarchy (no skipped levels, no more than one h1)
    - Alt text on all img elements
    - Presence of a ``<main>`` landmark element

    Args:
        html_content: Full HTML string to analyse.

    Returns:
        JSON string with ``is_accessible`` (bool) and ``issues`` (list of strings).
    """
    issues: list[str] = []

    if not html_content or not html_content.strip():
        issues.append("HTML content is empty — no structure to validate.")
        return json.dumps({"is_accessible": False, "issues": issues})

    parser = _HeadingAltParser()
    parser.feed(html_content)

    # Check for multiple h1
    h1_count = parser.headings.count(1)
    if h1_count > 1:
        issues.append(
            f"Multiple h1 elements found ({h1_count}). A document should have exactly one h1."
        )

    # Check heading hierarchy — no level may be skipped
    if parser.headings:
        prev = parser.headings[0]
        for level in parser.headings[1:]:
            if level > prev + 1:
                issues.append(
                    f"Heading level skipped: h{prev} followed by h{level}. "
                    "Heading levels must not skip (e.g. h1 → h3 without h2)."
                )
            prev = level

    # Check alt text
    if parser.img_missing_alt > 0:
        issues.append(
            f"{parser.img_missing_alt} image(s) missing alt attribute. "
            "All <img> elements must have an alt attribute for screen readers."
        )

    # Check for main landmark
    if not parser.has_main:
        issues.append(
            "No <main> landmark element found. "
            "Resumes should wrap primary content in <main> for screen reader navigation."
        )

    return json.dumps({"is_accessible": len(issues) == 0, "issues": issues})


def evaluate_layout(html_content: str) -> str:
    """Evaluate visual hierarchy and section structure of HTML resume content.

    Awards points for each expected resume section found by scanning h2 text
    content for common section keywords. Returns an integer score 0-100.

    Args:
        html_content: Full HTML string to evaluate.

    Returns:
        JSON string with ``layout_score`` (int 0-100), ``sections_found`` (list),
        and ``suggestions`` (list of actionable strings).
    """
    if not html_content or not html_content.strip():
        return json.dumps(
            {
                "layout_score": 0,
                "sections_found": [],
                "suggestions": ["Add content to the resume — the HTML is empty."],
            }
        )

    parser = _SectionParser()
    parser.feed(html_content)

    sections_found: list[str] = []
    suggestions: list[str] = []
    score = 0

    # 20 points: h1 present (candidate name)
    if parser.has_h1:
        score += 20
    else:
        suggestions.append("Add an h1 element for the candidate's name.")

    # 20 points each: experience + education + skills (core sections)
    # 10 points: summary (optional but valued)
    points_map = {"experience": 20, "education": 20, "skills": 20, "summary": 10}

    for section_name, keywords in _SECTION_KEYWORDS.items():
        found = any(any(kw in h2_text for kw in keywords) for h2_text in parser.h2_texts)
        if found:
            sections_found.append(section_name)
            score += points_map[section_name]
        else:
            suggestions.append(
                f"Consider adding a '{section_name.title()}' section (h2 heading with "
                f"content) to improve resume completeness."
            )

    # 10 points: header element present
    if parser.has_header:
        score += 10
    else:
        suggestions.append(
            "Add a <header> element wrapping the candidate name and contact information."
        )

    return json.dumps(
        {
            "layout_score": min(score, 100),
            "sections_found": sections_found,
            "suggestions": suggestions,
        }
    )


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex colour string to an (R, G, B) tuple.

    Accepts 3-digit (#rgb) and 6-digit (#rrggbb) formats, with or without
    the leading ``#``.

    Args:
        hex_color: Hex colour string.

    Returns:
        (R, G, B) tuple of integers 0-255.

    Raises:
        ValueError: If the string is not a valid hex colour.
    """
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not all(c in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"Invalid hex colour: '{hex_color}'")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1 spec.

    Args:
        r: Red channel 0-255.
        g: Green channel 0-255.
        b: Blue channel 0-255.

    Returns:
        Relative luminance value 0.0 (black) to 1.0 (white).
    """

    def _linearise(c: int) -> float:
        srgb = c / 255.0
        return srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4

    return 0.2126 * _linearise(r) + 0.7152 * _linearise(g) + 0.0722 * _linearise(b)


def verify_contrast(foreground: str, background: str) -> str:
    """Calculate the WCAG contrast ratio between two hex colours.

    Uses the WCAG 2.1 relative luminance formula. The ratio is always
    expressed as the lighter colour over the darker (≥ 1.0).

    Args:
        foreground: Text colour as a hex string (e.g. ``'#000000'``).
        background: Background colour as a hex string (e.g. ``'#ffffff'``).

    Returns:
        JSON string with ``ratio`` (float), ``passes_aa_normal`` (bool, 4.5:1),
        and ``passes_aa_large`` (bool, 3:1). On invalid input, returns
        ``{"error": "..."}``.
    """
    try:
        fg_rgb = _hex_to_rgb(foreground)
        bg_rgb = _hex_to_rgb(background)
    except ValueError as exc:
        return json.dumps({"error": str(exc)})

    l1 = _relative_luminance(*fg_rgb)
    l2 = _relative_luminance(*bg_rgb)
    lighter, darker = max(l1, l2), min(l1, l2)
    ratio = round((lighter + 0.05) / (darker + 0.05), 4)

    return json.dumps(
        {
            "ratio": ratio,
            "passes_aa_normal": ratio >= 4.5,
            "passes_aa_large": ratio >= 3.0,
        }
    )


def check_print_quality(html_content: str) -> str:
    """Inspect HTML for inline styles that cause poor print rendering.

    Flags:
    - ``display:none`` — content invisible in print
    - ``overflow:hidden`` — content may be clipped

    Args:
        html_content: Full HTML string to inspect.

    Returns:
        JSON string with ``print_ready`` (bool) and ``issues`` (list of strings).
    """
    issues: list[str] = []

    if not html_content or not html_content.strip():
        issues.append("HTML content is empty — nothing to print.")
        return json.dumps({"print_ready": False, "issues": issues})

    parser = _StyleParser()
    parser.feed(html_content)

    for style in parser.style_attrs:
        # Normalise whitespace around : and ;
        normalised = re.sub(r"\s*:\s*", ":", style).replace(" ", "")
        if "display:none" in normalised:
            issues.append(
                "Element with 'display:none' detected. Hidden elements will not "
                "appear in print output — verify this is intentional."
            )
            break  # Report once per document

    overflow_clipping = False
    for style in parser.style_attrs:
        normalised = re.sub(r"\s*:\s*", ":", style).replace(" ", "")
        if "overflow:hidden" in normalised:
            overflow_clipping = True
            break

    if overflow_clipping:
        issues.append(
            "Element with 'overflow:hidden' detected. Combined with a fixed height, "
            "this can clip resume content during printing."
        )

    return json.dumps({"print_ready": len(issues) == 0, "issues": issues})


# ---------------------------------------------------------------------------
# HR Tool Definitions (JSON schemas forwarded to the Anthropic API)
# ---------------------------------------------------------------------------

CHECK_GRAMMAR_TOOL = ToolDefinition(
    name="check_grammar",
    description=(
        "Scan plain text resume content for common grammar and style issues: "
        "double spaces, sentences starting with lowercase after a period, and weak "
        "phrases such as 'responsible for' or 'helped with'. Returns a JSON object "
        "with has_issues (bool) and issues (list of strings describing each problem)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Plain text content of the resume to check.",
            },
        },
        "required": ["text"],
    },
)

VALIDATE_FORMATTING_TOOL = ToolDefinition(
    name="validate_formatting",
    description=(
        "Check plain text resume content for inconsistent date formatting. "
        "Detects when multiple date styles are mixed (e.g. 'January 2020' alongside "
        "'01/2020'). Returns a JSON object with is_consistent (bool) and issues "
        "(list of strings describing inconsistencies found)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Plain text content of the resume to validate.",
            },
        },
        "required": ["text"],
    },
)

ASSESS_PROFESSIONALISM_TOOL = ToolDefinition(
    name="assess_professionalism",
    description=(
        "Evaluate the professional tone of plain text resume content. Penalises "
        "first-person pronouns (I, me, my), contractions (don't, I've), and vague "
        "language ('helped', 'did stuff'). Returns a JSON object with "
        "professionalism_score (int 0-100), issues (list), and suggestions (list)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Plain text content of the resume to assess.",
            },
        },
        "required": ["text"],
    },
)

DETECT_PLACEHOLDERS_TOOL = ToolDefinition(
    name="detect_placeholders",
    description=(
        "Search plain text resume content for leftover template placeholders: "
        "Lorem ipsum, XXX markers, TODO/TBD, bracket placeholders such as [Name] or "
        "[Company], and example email addresses (e.g. user@example.com). Returns a "
        "JSON object with has_placeholders (bool) and placeholders_found (list of "
        "matched placeholder strings)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Plain text content of the resume to inspect.",
            },
        },
        "required": ["text"],
    },
)

# ---------------------------------------------------------------------------
# HR module-level constants
# ---------------------------------------------------------------------------

_WEAK_PHRASES: list[str] = [
    "responsible for",
    "helped with",
    "helped to",
    "helped out",
    "was involved in",
    "worked on",
    "assisted with",
    "assisted in",
    "tasked with",
    "duties included",
]

_VAGUE_PHRASES: list[str] = [
    "stuff",
    "things",
    "various",
    "etc",
    "and more",
]

_DATE_PATTERNS: list[tuple[str, str]] = [
    (
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        "Month YYYY",
    ),
    (r"\b(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b", "Mon YYYY"),
    (r"\b\d{2}/\d{4}\b", "MM/YYYY"),
    (r"\b\d{4}-\d{2}\b", "YYYY-MM"),
]

_PLACEHOLDER_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)\blorem\s+ipsum\b", "Lorem ipsum"),
    (r"\bXXX\b", "XXX marker"),
    (r"(?i)\bTODO\b", "TODO marker"),
    (r"(?i)\bTBD\b", "TBD marker"),
    (r"\[[A-Za-z][A-Za-z\s]{1,30}\]", "bracket placeholder"),
    (r"\b[\w.+-]+@example\.com\b", "example.com email"),
    (r"\b[\w.+-]+@your-?(?:email|domain|company)\.(?:com|org)\b", "template email"),
]

_CONTRACTION_RE = re.compile(
    r"\b\w+(?:n't|'ve|'re|'ll|'d|'m)\b",
    re.IGNORECASE,
)

_FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|myself|I'm|I've|I'll|I'd)\b")

# ---------------------------------------------------------------------------
# HR tool handler functions
# ---------------------------------------------------------------------------


def check_grammar(text: str) -> str:
    """Scan resume text for common grammar and style issues.

    Checks:
    - Double (or more) consecutive spaces
    - Sentences that begin with a lowercase letter after a period
    - Weak phrases such as "responsible for" or "helped with"

    Args:
        text: Plain text content of the resume.

    Returns:
        JSON string with ``has_issues`` (bool) and ``issues`` (list of strings).
    """
    issues: list[str] = []

    if not text or not text.strip():
        return json.dumps({"has_issues": False, "issues": issues})

    # Double spaces
    if re.search(r"  +", text):
        issues.append("Double (or extra) spaces detected. Use a single space between words.")

    # Lowercase start after period
    if re.search(r"\.\s+[a-z]", text):
        issues.append(
            "Sentence appears to start with a lowercase letter after a period. "
            "Each sentence should begin with a capital letter."
        )

    # Weak phrases
    text_lower = text.lower()
    for phrase in _WEAK_PHRASES:
        if phrase in text_lower:
            issues.append(
                f"Weak phrase detected: '{phrase}'. "
                "Replace with a strong action verb (e.g. 'Led', 'Built', 'Designed')."
            )

    return json.dumps({"has_issues": len(issues) > 0, "issues": issues})


def validate_formatting(text: str) -> str:
    """Check resume text for inconsistent date formatting.

    Detects when two or more distinct date styles appear in the same document,
    e.g. "January 2020" mixed with "01/2020".

    Args:
        text: Plain text content of the resume.

    Returns:
        JSON string with ``is_consistent`` (bool) and ``issues`` (list of strings).
    """
    if not text or not text.strip():
        return json.dumps({"is_consistent": True, "issues": []})

    styles_found: list[str] = []
    for pattern, label in _DATE_PATTERNS:
        if re.search(pattern, text):
            styles_found.append(label)

    if len(styles_found) <= 1:
        return json.dumps({"is_consistent": True, "issues": []})

    issue = (
        f"Mixed date formats detected: {', '.join(styles_found)}. "
        "Use a single consistent date format throughout the resume "
        "(e.g. 'Month YYYY' or 'MM/YYYY')."
    )
    return json.dumps({"is_consistent": False, "issues": [issue]})


def assess_professionalism(text: str) -> str:
    """Evaluate professional tone of resume text.

    Penalises:
    - First-person pronouns (I, me, my)
    - Contractions (don't, I've, etc.)
    - Vague or informal language ("stuff", "things")

    Starting score is 100; each category of issue deducts points.

    Args:
        text: Plain text content of the resume.

    Returns:
        JSON string with ``professionalism_score`` (int 0-100),
        ``issues`` (list), and ``suggestions`` (list).
    """
    if not text or not text.strip():
        return json.dumps({"professionalism_score": 0, "issues": [], "suggestions": []})

    issues: list[str] = []
    suggestions: list[str] = []
    score = 100

    # First-person pronouns (-20 if found)
    if _FIRST_PERSON_RE.search(text):
        score -= 20
        issues.append(
            "First-person pronouns detected (I, me, my). "
            "Resume bullet points should start with action verbs, not 'I'."
        )
        suggestions.append(
            "Remove first-person pronouns. Start bullets with action verbs "
            "(e.g. 'Led', 'Built', 'Reduced')."
        )

    # Contractions (-15 if found)
    if _CONTRACTION_RE.search(text):
        score -= 15
        issues.append(
            "Contractions detected (e.g. didn't, I've). Professional resumes should use full words."
        )
        suggestions.append("Expand contractions: 'didn't' → 'did not'.")

    # Vague phrases (-10 per phrase, max -30)
    vague_found = [p for p in _VAGUE_PHRASES if p in text.lower()]
    if vague_found:
        deduction = min(len(vague_found) * 10, 30)
        score -= deduction
        issues.append(
            f"Vague language detected: {', '.join(repr(p) for p in vague_found)}. "
            "Use specific, quantified statements."
        )
        suggestions.append("Replace vague terms with specific accomplishments and metrics.")

    # Weak action phrases (-10 if any found)
    weak_found = [p for p in _WEAK_PHRASES if p in text.lower()]
    if weak_found:
        score -= 10
        issues.append(
            f"Weak phrasing detected: {', '.join(repr(p) for p in weak_found)}. "
            "Lead with strong action verbs instead."
        )
        suggestions.append(
            "Replace weak phrases with impactful action verbs "
            "(e.g. 'Led', 'Built', 'Reduced', 'Launched')."
        )

    return json.dumps(
        {
            "professionalism_score": max(score, 0),
            "issues": issues,
            "suggestions": suggestions,
        }
    )


def detect_placeholders(text: str) -> str:
    """Search resume text for leftover template placeholder content.

    Checks for Lorem ipsum, XXX markers, TODO/TBD, bracket placeholders
    such as ``[Name]`` or ``[Company]``, and example email addresses.

    Args:
        text: Plain text content of the resume.

    Returns:
        JSON string with ``has_placeholders`` (bool) and
        ``placeholders_found`` (list of matched strings).
    """
    if not text or not text.strip():
        return json.dumps({"has_placeholders": False, "placeholders_found": []})

    found: list[str] = []
    for pattern, label in _PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            found.append(f"{label}: '{match}'")

    return json.dumps({"has_placeholders": len(found) > 0, "placeholders_found": found})

"""HR review agent tools.

These tools are registered with HRAgent and called by Claude via tool_use to
evaluate resume grammar, formatting consistency, professional tone, and the
presence of leftover template placeholder content.

All functions accept and return strings (JSON-encoded where structured) to
conform to the Anthropic tool result format.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
import re

from resume_builder.models.agent import ToolDefinition

# ---------------------------------------------------------------------------
# Tool Definitions (JSON schemas forwarded to the Anthropic API)
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
# Module-level constants
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
    (r"\[[A-Za-z][A-Za-z ]{1,30}\]", "bracket placeholder"),
    (r"\b[\w.+-]+@example\.com\b", "example.com email"),
    (r"\b[\w.+-]+@your-?(?:email|domain|company)\.(?:com|org)\b", "template email"),
]

_CONTRACTION_RE = re.compile(
    r"\b\w+(?:n't|'ve|'re|'ll|'d|'m)\b",
    re.IGNORECASE,
)

_FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|myself|I'm|I've|I'll|I'd)\b")

# ---------------------------------------------------------------------------
# Tool handler functions
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
    fp_matches = _FIRST_PERSON_RE.findall(text)
    if fp_matches:
        score -= 20
        fp_unique = list(dict.fromkeys(m.lower() for m in fp_matches))
        issues.append(
            f"First-person language detected ({', '.join(repr(p) for p in fp_unique)}). "
            "Remove first-person pronouns; use action-verb openings and third-person perspective."
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

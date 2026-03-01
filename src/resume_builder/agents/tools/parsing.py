"""Parser agent tools for LinkedIn CSV processing.

These tools are registered with ParserAgent and called by Claude via tool_use
to parse, normalize, and validate LinkedIn export data.

All functions accept and return strings (JSON-encoded where structured) to
conform to the Anthropic tool result format.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import csv
import io
import json
import re

from resume_builder.models.agent import ToolDefinition

# ---------------------------------------------------------------------------
# Tool Definitions (JSON schemas forwarded to the Anthropic API)
# ---------------------------------------------------------------------------

PARSE_CSV_TOOL = ToolDefinition(
    name="parse_csv",
    description=(
        "Parse raw CSV content from a LinkedIn export and return the rows as "
        "structured JSON. Use this to read profile, positions, skills, education, "
        "or other LinkedIn CSV files."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "csv_content": {
                "type": "string",
                "description": "Raw CSV text content to parse.",
            },
            "csv_type": {
                "type": "string",
                "enum": [
                    "profile",
                    "positions",
                    "skills",
                    "education",
                    "certifications",
                    "honors",
                    "languages",
                    "projects",
                    "publications",
                    "volunteer",
                ],
                "description": "Type of LinkedIn CSV export file.",
            },
        },
        "required": ["csv_content", "csv_type"],
    },
)

NORMALIZE_DATES_TOOL = ToolDefinition(
    name="normalize_dates",
    description=(
        "Normalize a date string to YYYY-MM format. Handles LinkedIn export "
        "formats including 'YYYY-MM', 'Month YYYY' (full name), and 'Mon YYYY' "
        "(abbreviated). Returns an empty string for blank or ongoing dates."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "date_str": {
                "type": "string",
                "description": (
                    "Date string to normalize, e.g. '2021-03', 'March 2021', "
                    "'Mar 2021', or '' for ongoing."
                ),
            },
        },
        "required": ["date_str"],
    },
)

EXTRACT_IMPLICIT_SKILLS_TOOL = ToolDefinition(
    name="extract_implicit_skills",
    description=(
        "Scan text for implicit technology skill mentions and return a JSON list "
        "of discovered skills. Useful for extracting skills from job descriptions "
        "or position summaries that are not in the explicit Skills CSV."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to search for implicit technology skill mentions.",
            },
        },
        "required": ["text"],
    },
)

VALIDATE_DATA_TOOL = ToolDefinition(
    name="validate_data",
    description=(
        "Validate JSON data for the presence of required fields. Returns a JSON "
        "object with is_valid, missing_fields list, and completeness_percent (0-100)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "JSON string of the data object to validate.",
            },
            "required_fields": {
                "type": "string",
                "description": "JSON array of field names that must be present.",
            },
        },
        "required": ["data", "required_fields"],
    },
)

# ---------------------------------------------------------------------------
# Skill keyword dictionary for implicit extraction
# ---------------------------------------------------------------------------

_SKILL_KEYWORDS: frozenset[str] = frozenset(
    {
        # Programming languages
        "python",
        "java",
        "javascript",
        "typescript",
        "go",
        "rust",
        "c++",
        "c#",
        "ruby",
        "php",
        "swift",
        "kotlin",
        "scala",
        "r",
        # Frameworks and libraries
        "django",
        "flask",
        "fastapi",
        "react",
        "vue",
        "angular",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
        "spring",
        "express",
        "node.js",
        ".net",
        "pandas",
        "numpy",
        # Tools and platforms
        "docker",
        "kubernetes",
        "git",
        "jenkins",
        "terraform",
        "ansible",
        "grafana",
        "prometheus",
        "jira",
        # Cloud
        "aws",
        "gcp",
        "azure",
        # Databases
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "elasticsearch",
        "dynamodb",
        "cassandra",
    }
)

# ---------------------------------------------------------------------------
# Month name → number mapping for date normalization
# ---------------------------------------------------------------------------

_MONTH_NAMES: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------


def parse_csv(csv_content: str, csv_type: str) -> str:
    """Parse raw CSV content and return structured JSON data.

    Reads the CSV rows using the standard library ``csv.DictReader`` and
    returns a JSON object containing the csv_type, row count, and rows.

    Args:
        csv_content: Raw CSV text to parse.
        csv_type: LinkedIn export type identifier (e.g. ``"profile"``).

    Returns:
        JSON string with keys ``csv_type``, ``count``, and ``rows`` on
        success, or ``{"error": "..."}`` on failure.
    """
    if not csv_content or not csv_content.strip():
        return json.dumps({"error": "CSV content is empty"})

    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = [dict(row) for row in reader]
        return json.dumps({"csv_type": csv_type, "count": len(rows), "rows": rows})
    except csv.Error as exc:
        return json.dumps({"error": str(exc)})


def normalize_dates(date_str: str) -> str:
    """Normalize a date string to YYYY-MM format.

    Handles three common formats from LinkedIn exports:

    - ``YYYY-MM`` — passed through unchanged.
    - ``Month YYYY`` or ``Mon YYYY`` — converted using the month name map.
    - Empty string, ``"Present"``, or unrecognized — returns ``""``.

    Args:
        date_str: Date string to normalize.

    Returns:
        Normalized ``"YYYY-MM"`` string, or ``""`` for empty / present dates.
    """
    stripped = date_str.strip() if date_str else ""

    if not stripped or stripped.lower() == "present":
        return ""

    # Already YYYY-MM?
    if re.fullmatch(r"\d{4}-\d{2}", stripped):
        return stripped

    # "Month YYYY" or "Mon YYYY"
    parts = stripped.split()
    if len(parts) == 2:
        month_name, year_str = parts[0].lower(), parts[1]
        month_num = _MONTH_NAMES.get(month_name)
        if month_num and re.fullmatch(r"\d{4}", year_str):
            return f"{year_str}-{month_num:02d}"

    return ""


def extract_implicit_skills(text: str) -> str:
    """Scan text for implicit technology skill mentions.

    Uses word-boundary regex matching against a curated set of known
    technology keywords (case-insensitive, deduplicated).

    Args:
        text: Text to search (job description, position summary, etc.).

    Returns:
        JSON string containing a list of matched skill names (lowercase).
    """
    if not text:
        return json.dumps([])

    text_lower = text.lower()
    found: list[str] = []
    for skill in _SKILL_KEYWORDS:
        # Use word-boundary matching to avoid partial matches
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_lower):
            found.append(skill)

    return json.dumps(sorted(found))


def validate_data(data: str, required_fields: str) -> str:
    """Validate a JSON data object for the presence of required fields.

    Args:
        data: JSON string of the object to validate.
        required_fields: JSON string of a list of required field names.

    Returns:
        JSON string with keys ``is_valid`` (bool), ``missing_fields`` (list),
        and ``completeness_percent`` (float 0-100). On parse error, returns
        ``{"error": "..."}`` instead.
    """
    try:
        parsed_data: dict[str, object] = json.loads(data)
        fields: list[str] = json.loads(required_fields)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    missing = [f for f in fields if f not in parsed_data]
    total = len(fields)
    completeness = 100.0 if total == 0 else round((total - len(missing)) / total * 100, 2)

    return json.dumps(
        {
            "is_valid": len(missing) == 0,
            "missing_fields": missing,
            "completeness_percent": completeness,
        }
    )

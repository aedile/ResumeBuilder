"""Matcher agent tools for job description analysis and resume scoring.

These tools are registered with MatcherAgent and called by Claude via tool_use
to extract job requirements, score skill matches, identify gaps, and rank
experience by relevance.

All functions accept and return strings (JSON-encoded where structured) to
conform to the Anthropic tool result format.

CONSTITUTION Priority 0: No secrets or PII committed
CONSTITUTION Priority 5: Type hints, docstrings
"""

from __future__ import annotations

import json
import re
from typing import Any

from resume_builder.agents.tools.parsing import _SKILL_KEYWORDS
from resume_builder.models.agent import ToolDefinition

# ---------------------------------------------------------------------------
# Tool Definitions (JSON schemas forwarded to the Anthropic API)
# ---------------------------------------------------------------------------

EXTRACT_REQUIREMENTS_TOOL = ToolDefinition(
    name="extract_requirements",
    description=(
        "Parse a job description text and extract structured requirements including "
        "required technical skills, years of experience, and education level. "
        "Returns a JSON object with required_skills (list), years_experience (int or null), "
        "and education (string or null)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "job_text": {
                "type": "string",
                "description": "Full text of the job posting to analyse.",
            },
        },
        "required": ["job_text"],
    },
)

SCORE_MATCH_TOOL = ToolDefinition(
    name="score_match",
    description=(
        "Calculate a match score (0-100) between a resume's skills and a job's "
        "required skills. Returns a JSON object with score (int), matching_skills "
        "(list of skills present in both), and total_required (int)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "resume_skills": {
                "type": "string",
                "description": "JSON array of skill strings from the resume.",
            },
            "required_skills": {
                "type": "string",
                "description": "JSON array of skill strings required by the job.",
            },
        },
        "required": ["resume_skills", "required_skills"],
    },
)

IDENTIFY_GAPS_TOOL = ToolDefinition(
    name="identify_gaps",
    description=(
        "Identify skills required by the job that are absent from the resume. "
        "Returns a JSON array of missing skill strings."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "resume_skills": {
                "type": "string",
                "description": "JSON array of skill strings from the resume.",
            },
            "required_skills": {
                "type": "string",
                "description": "JSON array of skill strings required by the job.",
            },
        },
        "required": ["resume_skills", "required_skills"],
    },
)

RANK_EXPERIENCE_TOOL = ToolDefinition(
    name="rank_experience",
    description=(
        "Rank a list of resume positions by relevance to a set of job keywords. "
        "Returns a JSON array of position objects sorted by relevance score "
        "(highest first), each containing title, score, and matched_keywords."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "positions": {
                "type": "string",
                "description": (
                    "JSON array of position objects, each with 'title' (string) "
                    "and 'description' (string)."
                ),
            },
            "keywords": {
                "type": "string",
                "description": "JSON array of keyword strings to match against.",
            },
        },
        "required": ["positions", "keywords"],
    },
)

# ---------------------------------------------------------------------------
# Education pattern matching
# ---------------------------------------------------------------------------

_EDUCATION_PATTERNS: list[str] = [
    r"ph\.?d\.?",
    r"doctor(?:ate|al)",
    r"master['']?s?\s+(?:degree|of\s+\w+)?",
    r"m\.s\.",
    r"m\.b\.a\.",
    r"mba",
    r"bachelor['']?s?\s+(?:degree|of\s+\w+)?",
    r"b\.s\.",
    r"b\.a\.",
    r"associate['']?s?\s+(?:degree)?",
]

# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------


def extract_requirements(job_text: str) -> str:
    """Extract structured requirements from a job description.

    Scans the text for known technology skill keywords, years-of-experience
    patterns, and education-level phrases.

    Args:
        job_text: Full job posting text.

    Returns:
        JSON string with keys ``required_skills`` (list[str]),
        ``years_experience`` (int | None), and ``education`` (str | None).
    """
    if not job_text or not job_text.strip():
        return json.dumps({"required_skills": [], "years_experience": None, "education": None})

    text_lower = job_text.lower()

    # Extract skills using word-boundary matching (same approach as parsing tools)
    skills: list[str] = []
    for skill in _SKILL_KEYWORDS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_lower):
            skills.append(skill)

    # Extract years of experience from patterns like "5+ years", "5 years", "5 to 7 years"
    years_experience: int | None = None
    years_match = re.search(r"(\d+)\+?\s+years?", text_lower)
    if years_match:
        years_experience = int(years_match.group(1))

    # Extract education requirement
    education: str | None = None
    for edu_pattern in _EDUCATION_PATTERNS:
        edu_match = re.search(edu_pattern, text_lower)
        if edu_match:
            education = edu_match.group(0).strip()
            break

    return json.dumps(
        {
            "required_skills": sorted(skills),
            "years_experience": years_experience,
            "education": education,
        }
    )


def score_match(resume_skills: str, required_skills: str) -> str:
    """Score the overlap between resume skills and job-required skills.

    Comparison is case-insensitive. Returns 100 when no skills are required.

    Args:
        resume_skills: JSON string of a list of skill names from the resume.
        required_skills: JSON string of a list of skill names required by the job.

    Returns:
        JSON string with keys ``score`` (int 0-100), ``matching_skills`` (list[str]),
        and ``total_required`` (int). On parse error, returns ``{"error": "..."}``.
    """
    try:
        resume: list[str] = json.loads(resume_skills)
        required: list[str] = json.loads(required_skills)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    if not required:
        return json.dumps({"score": 100, "matching_skills": [], "total_required": 0})

    resume_lower = {s.lower() for s in resume}
    matched = [r for r in required if r.lower() in resume_lower]
    score = round(len(matched) / len(required) * 100)

    return json.dumps(
        {
            "score": score,
            "matching_skills": matched,
            "total_required": len(required),
        }
    )


def identify_gaps(resume_skills: str, required_skills: str) -> str:
    """Identify required skills absent from the resume.

    Comparison is case-insensitive.

    Args:
        resume_skills: JSON string of a list of skill names from the resume.
        required_skills: JSON string of a list of skill names required by the job.

    Returns:
        JSON string of a list of missing skill strings.
        On parse error, returns ``{"error": "..."}``.
    """
    try:
        resume: list[str] = json.loads(resume_skills)
        required: list[str] = json.loads(required_skills)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    resume_lower = {s.lower() for s in resume}
    gaps = [r for r in required if r.lower() not in resume_lower]
    return json.dumps(gaps)


def rank_experience(positions: str, keywords: str) -> str:
    """Rank resume positions by keyword relevance.

    Each position is scored by counting how many keywords appear (case-insensitively)
    in its combined title and description text. Positions are returned sorted by
    score descending.

    Args:
        positions: JSON string of a list of position objects, each with ``title``
            (str) and ``description`` (str).
        keywords: JSON string of a list of keyword strings.

    Returns:
        JSON string of a list of ranked position objects, each containing
        ``title`` (str), ``score`` (int), and ``matched_keywords`` (list[str]).
        On parse error, returns ``{"error": "..."}``.
    """
    try:
        pos_list: list[dict[str, str]] = json.loads(positions)
        kw_list: list[str] = json.loads(keywords)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    if not pos_list:
        return json.dumps([])

    kw_lower = [k.lower() for k in kw_list]

    ranked: list[dict[str, Any]] = []
    for pos in pos_list:
        combined = f"{pos.get('title', '')} {pos.get('description', '')}".lower()
        matched_kw = [k for k in kw_lower if re.search(rf"\b{re.escape(k)}\b", combined)]
        ranked.append(
            {
                "title": pos.get("title", ""),
                "score": len(matched_kw),
                "matched_keywords": matched_kw,
            }
        )

    ranked.sort(key=lambda p: p["score"], reverse=True)
    return json.dumps(ranked)

"""Optimizer agent tools for resume content improvement.

These tools are registered with OptimizerAgent and called by Claude via
tool_use to rewrite bullet points, generate tailored summaries, suggest
content edits, and verify factual accuracy.

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

REWRITE_BULLET_TOOL = ToolDefinition(
    name="rewrite_bullet",
    description=(
        "Rewrite a resume bullet point to be more impactful by starting with a "
        "strong action verb, incorporating relevant keywords, and suggesting "
        "quantifiable metrics. Returns the original and rewritten bullet with "
        "a list of improvement notes."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "bullet": {
                "type": "string",
                "description": "The original bullet point text to improve.",
            },
            "keywords": {
                "type": "string",
                "description": "JSON array of job-relevant keywords to incorporate.",
            },
        },
        "required": ["bullet", "keywords"],
    },
)

GENERATE_SUMMARY_TOOL = ToolDefinition(
    name="generate_summary",
    description=(
        "Generate a tailored professional summary for a resume, incorporating "
        "the candidate's top skills, target job title, and years of experience. "
        "Returns a JSON object with a 'summary' string field."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "skills": {
                "type": "string",
                "description": "JSON array of the candidate's top skill strings.",
            },
            "job_title": {
                "type": "string",
                "description": "Target job title to tailor the summary toward.",
            },
            "years_experience": {
                "type": "string",
                "description": "Years of relevant experience as a string (e.g. '5').",
            },
        },
        "required": ["skills", "job_title", "years_experience"],
    },
)

SUGGEST_EDITS_TOOL = ToolDefinition(
    name="suggest_edits",
    description=(
        "Analyse resume content against job requirements and suggest specific edits "
        "to better align with the role. Returns a JSON object with 'suggestions' "
        "(list of strings) and 'priority' ('high', 'medium', or 'low')."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Resume text section to analyse.",
            },
            "requirements": {
                "type": "string",
                "description": "JSON array of job requirement keyword strings.",
            },
        },
        "required": ["content", "requirements"],
    },
)

VERIFY_FACTS_TOOL = ToolDefinition(
    name="verify_facts",
    description=(
        "Verify that a resume claim is supported by the candidate's source data. "
        "Prevents fabrication by checking claims against factual source content. "
        "Returns a JSON object with 'is_supported' (bool), 'confidence' "
        "('high', 'medium', 'low'), and 'evidence' (string)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "claim": {
                "type": "string",
                "description": "The resume claim to verify.",
            },
            "source_data": {
                "type": "string",
                "description": "The original source data (LinkedIn export text) to check against.",
            },
        },
        "required": ["claim", "source_data"],
    },
)

# ---------------------------------------------------------------------------
# Action verbs for bullet point improvement
# ---------------------------------------------------------------------------

_ACTION_VERBS: list[str] = [
    "Architected",
    "Built",
    "Championed",
    "Delivered",
    "Designed",
    "Developed",
    "Drove",
    "Engineered",
    "Enhanced",
    "Established",
    "Implemented",
    "Improved",
    "Launched",
    "Led",
    "Managed",
    "Optimized",
    "Reduced",
    "Refactored",
    "Scaled",
    "Streamlined",
]

# Weak opening phrases to detect and replace
_WEAK_OPENERS: list[str] = [
    "worked on",
    "helped with",
    "assisted with",
    "was responsible for",
    "involved in",
    "participated in",
    "did",
    "handled",
    "dealt with",
    "contributed to",
]

# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------


def rewrite_bullet(bullet: str, keywords: str) -> str:
    """Rewrite a resume bullet point for maximum impact.

    Checks whether the bullet starts with a strong action verb. If not,
    prepends an appropriate action verb. Incorporates job-relevant keywords
    into the improvement notes when they are absent from the original text.

    Args:
        bullet: Original bullet point text.
        keywords: JSON string of a list of job-relevant keywords.

    Returns:
        JSON string with keys ``original`` (str), ``rewritten`` (str), and
        ``improvements`` (list[str]). On error, returns ``{"error": "..."}``.
    """
    if not bullet or not bullet.strip():
        return json.dumps({"error": "Bullet text is empty"})

    try:
        kw_list: list[str] = json.loads(keywords)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid keywords JSON: {exc}"})

    bullet_stripped = bullet.strip()
    bullet_lower = bullet_stripped.lower()
    improvements: list[str] = []

    # Check for weak opening phrases
    rewritten = bullet_stripped
    for weak in _WEAK_OPENERS:
        if bullet_lower.startswith(weak):
            # Replace with a strong action verb
            remainder = bullet_stripped[len(weak) :].strip()
            rewritten = f"Developed {remainder}"
            improvements.append(f"Replaced weak opener '{weak}' with action verb")
            break
    else:
        # Check if first word is already an action verb (starts with capital letter)
        first_word = bullet_stripped.split()[0] if bullet_stripped.split() else ""
        if not first_word[0].isupper() or first_word.lower() not in [
            v.lower() for v in _ACTION_VERBS
        ]:
            rewritten = f"Led {bullet_stripped[0].lower()}{bullet_stripped[1:]}"
            improvements.append("Added action verb at start of bullet")

    # Note missing keywords
    bullet_lower_full = bullet_stripped.lower()
    missing_kw = [k for k in kw_list if k.lower() not in bullet_lower_full]
    if missing_kw:
        improvements.append(f"Consider adding keywords: {', '.join(missing_kw)}")

    # Suggest metric if no numbers present
    if not re.search(r"\d", bullet_stripped):
        improvements.append("Add quantifiable metrics (%, $, time saved, team size)")

    return json.dumps(
        {
            "original": bullet_stripped,
            "rewritten": rewritten,
            "improvements": improvements,
        }
    )


def generate_summary(skills: str, job_title: str, years_experience: str) -> str:
    """Generate a tailored professional summary for a resume.

    Constructs a concise professional summary using the candidate's skills,
    target job title, and years of experience.

    Args:
        skills: JSON string of a list of skill name strings.
        job_title: Target position title.
        years_experience: Years of relevant experience (as a string).

    Returns:
        JSON string with key ``summary`` (str).
        On error, returns ``{"error": "..."}``.
    """
    try:
        skill_list: list[str] = json.loads(skills)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid skills JSON: {exc}"})

    years = years_experience.strip() if years_experience else "several"

    if skill_list:
        top_skills = ", ".join(skill_list[:3])
        if len(skill_list) > 3:
            top_skills += f", and {len(skill_list) - 3} more technologies"
        skills_phrase = f" specializing in {top_skills}"
    else:
        skills_phrase = ""

    summary = (
        f"Results-driven {job_title} with {years} years of experience"
        f"{skills_phrase}. "
        f"Proven track record of delivering high-quality software solutions "
        f"and driving technical excellence in collaborative team environments."
    )

    return json.dumps({"summary": summary})


def suggest_edits(content: str, requirements: str) -> str:
    """Suggest edits to resume content based on job requirements.

    Identifies job requirement keywords missing from the content and
    recommends additions to improve alignment with the target role.

    Args:
        content: Resume text section to analyse.
        requirements: JSON string of a list of job requirement keyword strings.

    Returns:
        JSON string with keys ``suggestions`` (list[str]) and ``priority``
        (``"high"``, ``"medium"``, or ``"low"``).
        On error, returns ``{"error": "..."}``.
    """
    try:
        req_list: list[str] = json.loads(requirements)
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid requirements JSON: {exc}"})

    content_lower = content.lower() if content else ""
    suggestions: list[str] = []

    for req in req_list:
        if req.lower() not in content_lower:
            suggestions.append(f"Consider adding '{req}' to demonstrate relevant experience")

    # Determine priority by ratio of missing requirements
    total = len(req_list)
    missing = len(suggestions)
    if total == 0 or missing == 0:
        priority = "low"
    elif missing / total >= 0.6:
        priority = "high"
    elif missing / total >= 0.3:
        priority = "medium"
    else:
        priority = "low"

    return json.dumps({"suggestions": suggestions, "priority": priority})


def verify_facts(claim: str, source_data: str) -> str:
    """Verify that a resume claim is grounded in source data.

    Uses word-level overlap to determine whether the key terms in a claim
    appear in the source data. A claim is supported when the majority of its
    meaningful words are found in the source.

    Args:
        claim: The resume claim to verify.
        source_data: Original source text (e.g. LinkedIn export data).

    Returns:
        JSON string with keys ``is_supported`` (bool), ``confidence``
        (``"high"``, ``"medium"``, or ``"low"``), and ``evidence`` (str).
        On error, returns ``{"error": "..."}``.
    """
    if not claim or not claim.strip():
        return json.dumps({"error": "Claim text is empty"})

    if not source_data or not source_data.strip():
        return json.dumps(
            {
                "is_supported": False,
                "confidence": "high",
                "evidence": "No source data provided to verify against.",
            }
        )

    claim_lower = claim.lower()
    source_lower = source_data.lower()

    # Extract meaningful words from claim (skip short stop words)
    stop_words: set[str] = {"a", "an", "the", "of", "in", "at", "on", "and", "or", "is", "was"}
    claim_words = [
        w for w in re.findall(r"\b\w+\b", claim_lower) if w not in stop_words and len(w) > 2
    ]

    if not claim_words:
        return json.dumps(
            {
                "is_supported": False,
                "confidence": "low",
                "evidence": "No meaningful terms found in claim to verify.",
            }
        )

    matched = [w for w in claim_words if w in source_lower]
    ratio = len(matched) / len(claim_words)

    is_supported = ratio >= 0.5
    if ratio >= 0.8:
        confidence: str = "high"
    elif ratio >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    if matched:
        evidence = f"Found matching terms in source: {', '.join(matched[:5])}"
    else:
        evidence = "No matching terms found in source data."

    return json.dumps(
        {
            "is_supported": is_supported,
            "confidence": confidence,
            "evidence": evidence,
        }
    )

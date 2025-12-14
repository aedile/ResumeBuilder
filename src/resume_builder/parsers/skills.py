"""CSV parser for LinkedIn Skills.csv export."""

from __future__ import annotations

import csv
from pathlib import Path

from resume_builder.models.resume import Skill

# Skill categorization mappings
SKILL_CATEGORIES: dict[str, list[str]] = {
    "Programming Languages": [
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
        "matlab",
    ],
    "Frameworks": [
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
    ],
    "Tools": [
        "docker",
        "kubernetes",
        "git",
        "jenkins",
        "terraform",
        "ansible",
        "grafana",
        "prometheus",
        "jira",
        "confluence",
    ],
    "Cloud Platforms": [
        "aws",
        "gcp",
        "google cloud",
        "google cloud platform",
        "azure",
        "cloud",
    ],
    "Databases": [
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "elasticsearch",
        "dynamodb",
        "cassandra",
        "oracle",
    ],
}


def _categorize_skill(skill_name: str) -> str | None:
    """Categorize a skill based on common keywords.

    Uses simple keyword matching against known skill categories.
    Matching is case-insensitive.

    Args:
        skill_name: Name of the skill to categorize.

    Returns:
        Category name if skill matches known category, None otherwise.

    Examples:
        >>> _categorize_skill("Python")
        'Programming Languages'
        >>> _categorize_skill("React")
        'Frameworks'
        >>> _categorize_skill("Unknown Skill")
        None
    """
    skill_lower = skill_name.lower()

    for category, keywords in SKILL_CATEGORIES.items():
        if skill_lower in keywords:
            return category

    return None


def parse_skills(csv_path: Path, categorize: bool = False) -> list[Skill]:
    """Parse LinkedIn Skills.csv into list of Skill models.

    Parses skills from LinkedIn export with optional auto-categorization
    for common programming languages, frameworks, tools, and platforms.
    Removes duplicate skills (case-insensitive).

    Args:
        csv_path: Path to Skills.csv file.
        categorize: If True, auto-categorize common skills. Defaults to False.

    Returns:
        List of Skill models with duplicates removed.
        Returns empty list if CSV has no skill rows.

    Raises:
        FileNotFoundError: If CSV file doesn't exist.
        ValueError: If CSV is malformed or missing required fields.

    Examples:
        >>> skills = parse_skills(Path("data/Skills.csv"))
        >>> len(skills)
        26
        >>> skills = parse_skills(Path("data/Skills.csv"), categorize=True)
        >>> skills[0].category
        'Programming Languages'
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Skills CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if not rows:
            return []

        # Validate required field
        if rows:
            first_row = rows[0]
            if "Name" not in first_row:
                raise ValueError("Missing required field: Name")

        # Track seen skills for deduplication (case-insensitive)
        seen_skills: set[str] = set()
        skills: list[Skill] = []

        for row in rows:
            skill_name = row.get("Name", "").strip()
            if not skill_name:
                continue

            # Check for duplicates (case-insensitive)
            skill_name_lower = skill_name.lower()
            if skill_name_lower in seen_skills:
                continue

            seen_skills.add(skill_name_lower)

            # Optionally categorize the skill
            category = _categorize_skill(skill_name) if categorize else None

            skill = Skill(name=skill_name, category=category)
            skills.append(skill)

        return skills

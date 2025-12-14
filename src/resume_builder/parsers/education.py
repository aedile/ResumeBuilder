"""CSV parser for LinkedIn Education.csv export."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from resume_builder.models.resume import Education


def _parse_year(year_str: str) -> date | None:
    """Parse year string to date (January 1st of that year).

    LinkedIn Education exports use years only (e.g., "2010").

    Args:
        year_str: Year string or empty string.

    Returns:
        Date object (January 1st), or None if empty/invalid.
    """
    if not year_str or not year_str.strip():
        return None

    try:
        year = int(year_str.strip())
        return date(year, 1, 1)
    except ValueError:
        return None


def parse_education(csv_path: Path) -> list[Education]:
    """Parse LinkedIn Education.csv into list of Education models.

    Args:
        csv_path: Path to Education.csv file.

    Returns:
        List of Education models. Returns empty list if file doesn't exist.

    Raises:
        ValueError: If CSV is malformed or missing required fields.
    """
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if not rows:
            return []

        # Validate required fields
        if rows:
            first_row = rows[0]
            if "School Name" not in first_row:
                raise ValueError("Missing required field: School Name")

        education_list: list[Education] = []

        for row in rows:
            school = row.get("School Name", "").strip()
            degree = row.get("Degree Name", "").strip()
            if not school or not degree:
                continue

            edu = Education(
                school_name=school,
                degree_name=degree,
                start_year=int(row["Start Date"]) if row.get("Start Date") else None,
                end_year=int(row["End Date"]) if row.get("End Date") else None,
                activities=row.get("Activities") or None,
            )
            education_list.append(edu)

        return education_list

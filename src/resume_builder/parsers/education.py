"""CSV parser for LinkedIn Education.csv export."""

from __future__ import annotations

import csv
from pathlib import Path

from resume_builder.models.resume import Education


def _parse_year_int(year_str: str | None) -> int | None:
    """Parse a year string to int, degrading gracefully on invalid input.

    LinkedIn Education exports use year-only strings (e.g. ``"2010"``), but
    can also contain non-numeric values such as ``"Present"`` or malformed
    date strings. Returns ``None`` for any value that cannot be parsed as a
    plain integer.

    Args:
        year_str: Year string from the CSV, or ``None`` / empty string.

    Returns:
        Integer year, or ``None`` if the value is absent or non-numeric.
    """
    if not year_str or not year_str.strip():
        return None
    try:
        return int(year_str.strip())
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
                start_year=_parse_year_int(row.get("Start Date")),
                end_year=_parse_year_int(row.get("End Date")),
                activities=row.get("Activities") or None,
            )
            education_list.append(edu)

        return education_list

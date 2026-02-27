"""CSV parser for LinkedIn Positions.csv export."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from resume_builder.models.resume import Position


def _parse_linkedin_date(date_str: str) -> date | None:
    """Parse LinkedIn date format (YYYY-MM) to Python date.

    LinkedIn exports dates as "YYYY-MM" (e.g., "2021-03").
    We parse these as the first day of the month for consistency.

    Args:
        date_str: Date string in "YYYY-MM" format or empty string.

    Returns:
        Date object set to first day of month, or None if empty/invalid.

    Examples:
        >>> _parse_linkedin_date("2021-03")
        date(2021, 3, 1)
        >>> _parse_linkedin_date("")
        None
    """
    if not date_str or not date_str.strip():
        return None

    try:
        # Parse YYYY-MM and set to first day of month
        year_str, month_str = date_str.split("-")
        year = int(year_str)
        month = int(month_str)

        # Validate year format (must be 4 digits)
        if len(year_str) != 4:
            return None

        # Validate month range
        if not (1 <= month <= 12):
            return None

        return date(year, month, 1)
    except (ValueError, AttributeError):
        return None


def parse_positions(csv_path: Path) -> list[Position]:
    """Parse LinkedIn Positions.csv into list of Position models.

    Parses work history from LinkedIn export, handling date formats,
    multiline descriptions, and current positions (no end date).
    Results are sorted by start_date descending (newest first).

    Args:
        csv_path: Path to Positions.csv file.

    Returns:
        List of Position models sorted by start_date (newest first).
        Returns empty list if file is missing or CSV has no position rows.

    Raises:
        ValueError: If CSV is malformed or missing required fields.

    Examples:
        >>> positions = parse_positions(Path("data/Positions.csv"))
        >>> positions[0].company  # Most recent position
        'TechVision AI'
    """
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if not rows:
            return []

        # Validate required fields
        required_fields = ["Company Name", "Title", "Started On"]
        if rows:
            first_row = rows[0]
            missing = [f for f in required_fields if f not in first_row]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

        positions = []
        for row in rows:
            # Skip rows with missing required data
            if not row.get("Company Name") or not row.get("Title"):
                continue

            start_date = _parse_linkedin_date(row["Started On"])
            if start_date is None:
                continue  # Skip positions without valid start date

            position = Position(
                company=row["Company Name"],
                title=row["Title"],
                start_date=start_date,
                end_date=_parse_linkedin_date(row.get("Finished On", "")),
                description=row.get("Description") or None,
                location=row.get("Location") or None,
            )
            positions.append(position)

        # Sort by start_date descending (newest first)
        positions.sort(key=lambda p: p.start_date, reverse=True)

        return positions

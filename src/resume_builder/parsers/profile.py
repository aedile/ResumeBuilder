"""CSV parser for LinkedIn Profile.csv export."""

from __future__ import annotations

import csv
from pathlib import Path

from resume_builder.exceptions import ParseError
from resume_builder.models.resume import Profile


def parse_profile(csv_path: Path) -> Profile:
    """Parse LinkedIn Profile.csv into Profile model.

    Args:
        csv_path: Path to Profile.csv file.

    Returns:
        Profile model with parsed data.

    Raises:
        ParseError: If CSV file doesn't exist, is empty, or is missing required fields.
    """
    if not csv_path.exists():
        raise ParseError(f"Profile CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if not rows:
            raise ParseError("Profile CSV is empty")

        row = rows[0]  # Profile.csv has only one row

        # Validate required fields
        required_fields = ["First Name", "Last Name", "Headline"]
        missing = [f for f in required_fields if f not in row or not row[f]]
        if missing:
            raise ParseError(f"Missing required fields: {', '.join(missing)}")

        # Extract fields with fallback for optional
        return Profile(
            first_name=row["First Name"],
            last_name=row["Last Name"],
            headline=row["Headline"],
            summary=row.get("Summary") or None,
            industry=row.get("Industry") or None,
            location=row.get("Geo Location") or None,
        )

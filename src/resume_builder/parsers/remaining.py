"""Remaining LinkedIn CSV parsers - consolidated for efficiency."""

from __future__ import annotations

import csv
from pathlib import Path

from resume_builder.models.resume import (
    Certification,
    Honor,
    Language,
    Project,
    Publication,
    Volunteer,
)

# Reuse date parser from positions
from resume_builder.parsers.positions import _parse_linkedin_date


def parse_certifications(csv_path: Path) -> list[Certification]:
    """Parse Certifications.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Certification(
                name=row["Name"],
                authority=row["Authority"],  # Required field
                start_date=_parse_linkedin_date(row.get("Started On", "")),
                end_date=_parse_linkedin_date(row.get("Finished On", "")),
                url=row.get("Url"),
            )
            for row in reader
            if row.get("Name") and row.get("Authority")
        ]


def parse_projects(csv_path: Path) -> list[Project]:
    """Parse Projects.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Project(
                title=row["Title"],
                description=row["Description"],  # Required field
                url=row.get("Url"),
            )
            for row in reader
            if row.get("Title") and row.get("Description")
        ]


def parse_publications(csv_path: Path) -> list[Publication]:
    """Parse Publications.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Publication(
                title=row["Title"],
                publisher=row["Publisher"],  # Required field
                publication_date=_parse_linkedin_date(row.get("Published On", "")),
                url=row.get("Url"),
            )
            for row in reader
            if row.get("Title") and row.get("Publisher")
        ]


def parse_languages(csv_path: Path) -> list[Language]:
    """Parse Languages.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Language(name=row["Name"], proficiency=row.get("Proficiency"))
            for row in reader
            if row.get("Name")
        ]


def parse_honors(csv_path: Path) -> list[Honor]:
    """Parse Honors.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Honor(
                title=row["Title"],
                issuer=row["Issuer"],  # Required field
                date=None,  # TODO: LinkedIn format unclear, needs investigation
                description=row.get("Description"),
            )
            for row in reader
            if row.get("Title") and row.get("Issuer")
        ]


def parse_volunteer(csv_path: Path) -> list[Volunteer]:
    """Parse Volunteer.csv."""
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Volunteer(
                organization=row["Company Name"],
                role=row["Role"],  # Required field
                cause=row.get("Cause"),
                start_date=_parse_linkedin_date(row.get("Started On", "")),
                end_date=_parse_linkedin_date(row.get("Finished On", "")),
            )
            for row in reader
            if row.get("Company Name") and row.get("Role")
        ]

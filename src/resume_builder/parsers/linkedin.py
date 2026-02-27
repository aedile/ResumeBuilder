"""LinkedIn export parser orchestrator.

Coordinates all CSV parsers to build a complete Resume object from
a LinkedIn data export directory or ZIP file.
"""

from __future__ import annotations

from pathlib import Path

from resume_builder.exceptions import ExportNotFoundError, InvalidExportError
from resume_builder.models.resume import Resume
from resume_builder.parsers.certifications import parse_certifications
from resume_builder.parsers.education import parse_education
from resume_builder.parsers.honors import parse_honors
from resume_builder.parsers.languages import parse_languages
from resume_builder.parsers.positions import parse_positions
from resume_builder.parsers.profile import parse_profile
from resume_builder.parsers.projects import parse_projects
from resume_builder.parsers.publications import parse_publications
from resume_builder.parsers.skills import parse_skills
from resume_builder.parsers.volunteer import parse_volunteer


def parse_linkedin_export(export_path: Path) -> Resume:
    """Parse LinkedIn data export into a complete Resume object.

     Coordinates all individual CSV parsers and assembles them into
     a single Resume object. Handles partial exports gracefully by
     treating optional CSVs as empty lists if missing.

     Args:
         export_path: Path to LinkedIn export directory or ZIP file.

     Returns:
         Complete Resume object with all available data.

     Raises:
         ExportNotFoundError: If directory doesn't exist.
         InvalidExportError: If Profile.csv is missing from the export directory.

    Examples:
         >>> resume = parse_linkedin_export(Path("linkedin_export"))
         >>> resume.profile.full_name
         'John Doe'
         >>> len(resume.positions)
         5
    """
    if not export_path.exists():
        raise ExportNotFoundError(f"Directory not found: {export_path}")

    if not export_path.is_dir():
        msg = "ZIP file support not yet implemented"
        raise NotImplementedError(msg)

    # Profile.csv is required
    profile_csv = export_path / "Profile.csv"
    if not profile_csv.exists():
        raise InvalidExportError("Profile.csv is required in LinkedIn export")

    # Parse required Profile
    profile = parse_profile(profile_csv)

    # Parse all optional CSVs — all return [] if the file is missing
    positions = parse_positions(export_path / "Positions.csv")
    skills = parse_skills(export_path / "Skills.csv")
    education = parse_education(export_path / "Education.csv")
    certifications = parse_certifications(export_path / "Certifications.csv")
    projects = parse_projects(export_path / "Projects.csv")
    publications = parse_publications(export_path / "Publications.csv")
    languages = parse_languages(export_path / "Languages.csv")
    honors = parse_honors(export_path / "Honors.csv")
    volunteer = parse_volunteer(export_path / "Volunteer.csv")

    # Assemble Resume
    return Resume(
        profile=profile,
        positions=positions,
        education=education,
        skills=skills,
        certifications=certifications,
        projects=projects,
        publications=publications,
        languages=languages,
        honors=honors,
        volunteer=volunteer,
    )

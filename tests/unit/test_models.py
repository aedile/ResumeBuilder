"""Tests for resume data models.

TDD Approach: These tests are written FIRST (RED phase).
The models in src/resume_builder/models/resume.py will be
implemented to make these tests pass (GREEN phase).
"""

from datetime import date

import pytest
from pydantic import ValidationError

from resume_builder.models.resume import (
    Certification,
    Education,
    Position,
    Profile,
    Project,
    Publication,
    Resume,
    Skill,
)


class TestProfile:
    """Tests for the Profile model."""

    def test_profile_with_required_fields(self) -> None:
        """Profile can be created with required fields only."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Software Engineer",
        )
        assert profile.first_name == "Jane"
        assert profile.last_name == "Doe"
        assert profile.headline == "Software Engineer"
        assert profile.summary is None

    def test_profile_with_all_fields(self) -> None:
        """Profile can be created with all fields."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Software Engineer at TechCorp",
            summary="Experienced developer with 10+ years...",
            industry="Technology",
            location="San Francisco, CA",
        )
        assert profile.summary == "Experienced developer with 10+ years..."
        assert profile.industry == "Technology"
        assert profile.location == "San Francisco, CA"

    def test_profile_full_name_property(self) -> None:
        """Profile has a full_name property."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Engineer",
        )
        assert profile.full_name == "Jane Doe"

    def test_profile_requires_first_name(self) -> None:
        """Profile validation fails without first_name."""
        with pytest.raises(ValidationError):
            Profile(last_name="Doe", headline="Engineer")  # type: ignore[call-arg]


class TestPosition:
    """Tests for the Position (work experience) model."""

    def test_position_with_required_fields(self) -> None:
        """Position can be created with required fields."""
        position = Position(
            company="TechCorp",
            title="Software Engineer",
            start_date=date(2020, 1, 1),
        )
        assert position.company == "TechCorp"
        assert position.title == "Software Engineer"
        assert position.end_date is None  # Current position

    def test_position_with_end_date(self) -> None:
        """Position can have an end date."""
        position = Position(
            company="OldCorp",
            title="Junior Developer",
            start_date=date(2018, 6, 1),
            end_date=date(2019, 12, 31),
            description="Built web applications.",
            location="New York, NY",
        )
        assert position.end_date == date(2019, 12, 31)
        assert position.description == "Built web applications."
        assert position.location == "New York, NY"

    def test_position_is_current_property(self) -> None:
        """Position has is_current property based on end_date."""
        current = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
        )
        past = Position(
            company="OldCorp",
            title="Engineer",
            start_date=date(2018, 1, 1),
            end_date=date(2019, 12, 31),
        )
        assert current.is_current is True
        assert past.is_current is False

    def test_position_duration_property(self) -> None:
        """Position has a duration string property."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 1, 1),
        )
        # Should return something like "2 years" or "Jan 2020 - Jan 2022"
        assert position.duration is not None
        assert isinstance(position.duration, str)


class TestEducation:
    """Tests for the Education model."""

    def test_education_with_required_fields(self) -> None:
        """Education can be created with required fields."""
        education = Education(
            school_name="University of Technology",
            degree_name="Bachelor of Science",
        )
        assert education.school_name == "University of Technology"
        assert education.degree_name == "Bachelor of Science"

    def test_education_with_dates(self) -> None:
        """Education can have start and end years."""
        education = Education(
            school_name="University of Technology",
            degree_name="Bachelor of Science",
            start_year=2014,
            end_year=2018,
            activities="Dean's List, Computer Science Club",
        )
        assert education.start_year == 2014
        assert education.end_year == 2018
        assert education.activities == "Dean's List, Computer Science Club"


class TestSkill:
    """Tests for the Skill model."""

    def test_skill_creation(self) -> None:
        """Skill can be created with a name."""
        skill = Skill(name="Python")
        assert skill.name == "Python"

    def test_skill_with_category(self) -> None:
        """Skill can have an optional category."""
        skill = Skill(name="Python", category="Programming Languages")
        assert skill.category == "Programming Languages"


class TestCertification:
    """Tests for the Certification model."""

    def test_certification_creation(self) -> None:
        """Certification can be created with required fields."""
        cert = Certification(
            name="AWS Solutions Architect",
            authority="Amazon Web Services",
        )
        assert cert.name == "AWS Solutions Architect"
        assert cert.authority == "Amazon Web Services"

    def test_certification_with_dates(self) -> None:
        """Certification can have start and end dates."""
        cert = Certification(
            name="AWS Solutions Architect",
            authority="Amazon Web Services",
            start_date=date(2022, 1, 1),
            end_date=date(2025, 1, 1),
            url="https://aws.amazon.com/certification/",
        )
        assert cert.start_date == date(2022, 1, 1)
        assert cert.url == "https://aws.amazon.com/certification/"


class TestProject:
    """Tests for the Project model."""

    def test_project_creation(self) -> None:
        """Project can be created with required fields."""
        project = Project(
            title="Open Source Contribution",
            description="Built a CLI tool for data processing.",
        )
        assert project.title == "Open Source Contribution"
        assert project.description == "Built a CLI tool for data processing."

    def test_project_with_url(self) -> None:
        """Project can have a URL."""
        project = Project(
            title="Portfolio Website",
            description="Personal portfolio built with React.",
            url="https://github.com/user/portfolio",
        )
        assert project.url == "https://github.com/user/portfolio"


class TestPublication:
    """Tests for the Publication model."""

    def test_publication_creation(self) -> None:
        """Publication can be created with required fields."""
        pub = Publication(
            title="Machine Learning Best Practices",
            publisher="Tech Journal",
        )
        assert pub.title == "Machine Learning Best Practices"
        assert pub.publisher == "Tech Journal"

    def test_publication_with_date_and_url(self) -> None:
        """Publication can have date and URL."""
        pub = Publication(
            title="Machine Learning Best Practices",
            publisher="Tech Journal",
            publication_date=date(2023, 6, 15),
            url="https://techjournal.com/article/123",
        )
        assert pub.publication_date == date(2023, 6, 15)


class TestResume:
    """Tests for the aggregate Resume model."""

    def test_resume_creation_with_profile_only(self) -> None:
        """Resume can be created with just a profile."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Software Engineer",
        )
        resume = Resume(profile=profile)
        assert resume.profile == profile
        assert resume.positions == []
        assert resume.skills == []

    def test_resume_with_all_sections(self) -> None:
        """Resume can contain all sections."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Software Engineer",
        )
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
        )
        skill = Skill(name="Python")
        education = Education(
            school_name="University",
            degree_name="BS Computer Science",
        )

        resume = Resume(
            profile=profile,
            positions=[position],
            skills=[skill],
            education=[education],
            certifications=[],
            projects=[],
            publications=[],
        )

        assert len(resume.positions) == 1
        assert len(resume.skills) == 1
        assert len(resume.education) == 1

    def test_resume_positions_sorted_by_date(self) -> None:
        """Resume positions should be sorted with most recent first."""
        profile = Profile(
            first_name="Jane",
            last_name="Doe",
            headline="Engineer",
        )
        old_position = Position(
            company="OldCorp",
            title="Junior",
            start_date=date(2015, 1, 1),
            end_date=date(2018, 1, 1),
        )
        new_position = Position(
            company="NewCorp",
            title="Senior",
            start_date=date(2020, 1, 1),
        )

        resume = Resume(
            profile=profile,
            positions=[old_position, new_position],
        )

        # Most recent first
        assert resume.sorted_positions[0].company == "NewCorp"
        assert resume.sorted_positions[1].company == "OldCorp"

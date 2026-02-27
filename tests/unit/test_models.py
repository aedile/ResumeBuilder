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

    def test_position_duration_exactly_two_years(self) -> None:
        """Duration returns 'N years' when months remainder is zero."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 1, 1),
        )
        assert position.duration == "2 years"

    def test_position_duration_years_and_months(self) -> None:
        """Duration returns 'N years M months' when both are non-zero."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 4, 1),
        )
        assert position.duration == "2 years 3 months"

    def test_position_duration_months_only(self) -> None:
        """Duration returns 'N months' when under one year."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2022, 3, 1),
            end_date=date(2022, 9, 1),
        )
        assert position.duration == "6 months"

    def test_position_duration_negative_months_rollover(self) -> None:
        """Duration handles month subtraction correctly when crossing a year boundary."""
        # March 2020 -> January 2021: 10 months (not 1 year -2 months)
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 3, 1),
            end_date=date(2021, 1, 1),
        )
        assert position.duration == "10 months"

    def test_position_duration_less_than_one_month(self) -> None:
        """Duration returns 'Less than 1 month' for very short stints."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2022, 3, 1),
            end_date=date(2022, 3, 15),
        )
        assert position.duration == "Less than 1 month"

    def test_position_duration_current_returns_elapsed_time(self) -> None:
        """Duration for a current position returns elapsed time, not a date range."""
        # Start far enough back that we know there's meaningful elapsed time.
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 1, 1),
        )
        # Must NOT look like a date range (the old broken behaviour).
        assert " - Present" not in position.duration
        assert " - " not in position.duration
        # Must look like a duration (contains "years" or "months").
        assert "years" in position.duration or "months" in position.duration

    def test_position_date_range_ended_position(self) -> None:
        """date_range returns 'Mon YYYY - Mon YYYY' for ended positions."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 3, 1),
            end_date=date(2022, 1, 1),
        )
        assert position.date_range == "Mar 2020 - Jan 2022"

    def test_position_date_range_current_position(self) -> None:
        """date_range returns 'Mon YYYY - Present' for current positions."""
        position = Position(
            company="TechCorp",
            title="Engineer",
            start_date=date(2020, 3, 1),
        )
        assert position.date_range == "Mar 2020 - Present"


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

    def test_resume_positions_always_sorted_by_date(self) -> None:
        """resume.positions is always sorted newest-first regardless of insertion order."""
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

        # Insert in oldest-first order — positions should still come out newest-first.
        resume = Resume(
            profile=profile,
            positions=[old_position, new_position],
        )

        assert resume.positions[0].company == "NewCorp"
        assert resume.positions[1].company == "OldCorp"

    def test_resume_positions_sorted_three_entries(self) -> None:
        """Sorting works correctly for three positions in arbitrary insertion order."""
        profile = Profile(first_name="A", last_name="B", headline="C")
        positions = [
            Position(company="Mid", title="E", start_date=date(2017, 6, 1), end_date=date(2019, 1, 1)),
            Position(company="New", title="E", start_date=date(2021, 1, 1)),
            Position(company="Old", title="E", start_date=date(2012, 1, 1), end_date=date(2015, 1, 1)),
        ]
        resume = Resume(profile=profile, positions=positions)

        assert [p.company for p in resume.positions] == ["New", "Mid", "Old"]

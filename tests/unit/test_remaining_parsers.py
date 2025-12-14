"""Tests for Certifications, Projects, Publications, Languages, Honors, and Volunteer CSV parsers.

CONSTITUTION Priority 3: TDD RED Phase
CONSTITUTION Priority 4: 90%+ Coverage

Combined test file for efficiency given 6 similar parsers.
"""

from pathlib import Path

from resume_builder.parsers.certifications import parse_certifications
from resume_builder.parsers.honors import parse_honors
from resume_builder.parsers.languages import parse_languages
from resume_builder.parsers.projects import parse_projects
from resume_builder.parsers.publications import parse_publications
from resume_builder.parsers.volunteer import parse_volunteer


class TestCertificationsParser:
    """Tests for parse_certifications function."""

    def test_parse_valid_certifications(self, tmp_path: Path) -> None:
        """Parse valid Certifications.csv correctly."""
        csv_content = """Name,Url,Authority,Started On,Finished On,License Number
AWS ML Specialty,https://aws.amazon.com,Amazon,2022-03,,AWS-123
TensorFlow Dev,https://tensorflow.org,Google,2020-06,,TF-456
"""
        csv_file = tmp_path / "certs.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        certs = parse_certifications(csv_file)

        assert len(certs) == 2
        assert certs[0].name == "AWS ML Specialty"
        assert certs[0].authority == "Amazon"

    def test_parse_certifications_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_certifications(Path("/nonexistent.csv")) == []


class TestProjectsParser:
    """Tests for parse_projects function."""

    def test_parse_valid_projects(self, tmp_path: Path) -> None:
        """Parse valid Projects.csv correctly."""
        csv_content = """Title,Description,Url,Started On,Finished On
ML Pipeline,Open source framework,https://github.com/test,2019-06,2020-12
Fraud Detection,Real-time system,,2020-01,2020-08
"""
        csv_file = tmp_path / "projects.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        projects = parse_projects(csv_file)

        assert len(projects) == 2
        assert projects[0].title == "ML Pipeline"
        assert projects[0].url == "https://github.com/test"

    def test_parse_projects_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_projects(Path("/nonexistent.csv")) == []


class TestPublicationsParser:
    """Tests for parse_publications function."""

    def test_parse_valid_publications(self, tmp_path: Path) -> None:
        """Parse valid Publications.csv correctly."""
        csv_content = """Title,Publisher,Published On,Url,Description
Deep Learning Paper,IEEE,2021-06,https://arxiv.org,Research paper
ML Tutorial,Medium,2022-03,https://medium.com,Tutorial article
"""
        csv_file = tmp_path / "pubs.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        pubs = parse_publications(csv_file)

        assert len(pubs) == 2
        assert pubs[0].title == "Deep Learning Paper"
        assert pubs[0].publisher == "IEEE"

    def test_parse_publications_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_publications(Path("/nonexistent.csv")) == []


class TestLanguagesParser:
    """Tests for parse_languages function."""

    def test_parse_valid_languages(self, tmp_path: Path) -> None:
        """Parse valid Languages.csv correctly."""
        csv_content = """Name,Proficiency
English,Native or bilingual proficiency
Spanish,Professional working proficiency
Mandarin,Elementary proficiency
"""
        csv_file = tmp_path / "langs.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        langs = parse_languages(csv_file)

        assert len(langs) == 3
        assert langs[0].name == "English"
        assert langs[0].proficiency == "Native or bilingual proficiency"

    def test_parse_languages_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_languages(Path("/nonexistent.csv")) == []


class TestHonorsParser:
    """Tests for parse_honors function."""

    def test_parse_valid_honors(self, tmp_path: Path) -> None:
        """Parse valid Honors.csv correctly."""
        csv_content = """Title,Issuer,Issued On,Description
Dean's List,Stanford,2011-06,Academic achievement
Best Paper Award,ICML,2021-07,Research excellence
"""
        csv_file = tmp_path / "honors.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        honors = parse_honors(csv_file)

        assert len(honors) == 2
        assert honors[0].title == "Dean's List"
        assert honors[0].issuer == "Stanford"

    def test_parse_honors_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_honors(Path("/nonexistent.csv")) == []


class TestVolunteerParser:
    """Tests for parse_volunteer function."""

    def test_parse_valid_volunteer(self, tmp_path: Path) -> None:
        """Parse valid Volunteer.csv correctly."""
        csv_content = """Company Name,Role,Started On,Finished On,Description
Code for Good,Mentor,2020-01,2021-12,Teaching programming
Food Bank,Volunteer,2019-06,,Ongoing service
"""
        csv_file = tmp_path / "volunteer.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        vol = parse_volunteer(csv_file)

        assert len(vol) == 2
        assert vol[0].organization == "Code for Good"
        assert vol[0].role == "Mentor"
        assert vol[1].end_date is None  # Ongoing

    def test_parse_volunteer_missing_file_returns_empty(self) -> None:
        """Return empty list when file doesn't exist."""
        assert parse_volunteer(Path("/nonexistent.csv")) == []

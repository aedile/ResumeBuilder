"""Pytest configuration and fixtures for Resume Builder tests."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_data_dir() -> Path:
    """Return the path to the sample data directory."""
    return Path(__file__).parent.parent / "sample_data"


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to test-specific data fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def linkedin_fixtures_dir(test_data_dir: Path) -> Path:
    """Return the path to LinkedIn CSV fixtures."""
    return test_data_dir / "linkedin"


@pytest.fixture
def job_fixtures_dir(test_data_dir: Path) -> Path:
    """Return the path to job description fixtures."""
    return test_data_dir / "jobs"


@pytest.fixture
def api_fixtures_dir(test_data_dir: Path) -> Path:
    """Return the path to API response fixtures."""
    return test_data_dir / "api_responses"


@pytest.fixture
def load_fixture_csv(linkedin_fixtures_dir: Path):
    """Load a CSV fixture file."""

    def _load(filename: str) -> Path:
        path = linkedin_fixtures_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        return path

    return _load


@pytest.fixture
def load_fixture_json(api_fixtures_dir: Path):
    """Load a JSON fixture file."""

    def _load(filename: str) -> dict:
        path = api_fixtures_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        with path.open() as f:
            return json.load(f)

    return _load


@pytest.fixture
def load_fixture_text(job_fixtures_dir: Path):
    """Load a text fixture file."""

    def _load(filename: str) -> str:
        path = job_fixtures_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        return path.read_text()

    return _load

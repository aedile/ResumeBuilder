"""Pytest configuration and fixtures for Resume Builder tests."""

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

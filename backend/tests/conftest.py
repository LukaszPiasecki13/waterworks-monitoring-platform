"""Shared fixtures for backend tests."""

import pytest

from app.modules.core_data.registry import SensorRegistry


@pytest.fixture(scope="session", autouse=True)
def initialize_registry():
    """Initialize sensor registry at test session start."""
    SensorRegistry.initialize()
    yield

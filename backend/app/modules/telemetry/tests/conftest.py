"""Fixtures shared by telemetry tests.

Ingest validates point types, error codes and state sections against the
sensor registry, which production loads once at app startup (`lifespan`).
Tests build their own FastAPI app or call the service directly, so without
this the registry stays uninitialised and every ingest path fails on
`RegistryLoadError` instead of exercising the code under test.
"""

import pytest

from app.modules.core_data.registry import SensorRegistry


@pytest.fixture(autouse=True)
def sensor_registry_loaded() -> None:
    SensorRegistry.initialize()

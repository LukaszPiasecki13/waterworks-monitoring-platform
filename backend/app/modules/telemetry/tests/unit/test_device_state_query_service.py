"""Unit tests for the read side of the device state channel (B-08).

These pin the one rule the brief calls out explicitly: never present a device
value without saying how old it is.
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.telemetry.services.device_state import DeviceStateQueryService


def _report(captured_at: datetime, section: str = "device") -> SimpleNamespace:
    return SimpleNamespace(
        section=section,
        schema_version=1,
        captured_at=captured_at,
        received_at=captured_at + timedelta(seconds=1),
        data={"uptime_seconds": 42},
    )


@pytest.fixture
def device():
    return SimpleNamespace(
        id=uuid4(),
        external_id="WW-TEST-SN",
        last_seen_at=datetime.now(UTC),
        last_diagnostics_at=datetime.now(UTC),
    )


def _service(reports, device, stale_after_seconds: int = 300):
    repo = MagicMock()
    repo.list_latest_sections.return_value = reports

    device_service = MagicMock()
    device_service.get_by_id.return_value = device

    settings = SimpleNamespace(telemetry_stale_after_seconds=stale_after_seconds)
    return DeviceStateQueryService(repo, device_service, settings)


def test_age_is_measured_from_capture_not_arrival(device):
    captured = datetime.now(UTC) - timedelta(minutes=20)
    service = _service([_report(captured)], device)

    response = service.get_device_state(device.id)

    section = response.sections[0]
    assert 1190 <= section.age_seconds <= 1210
    assert section.is_stale is True


def test_fresh_report_is_not_stale(device):
    captured = datetime.now(UTC) - timedelta(seconds=30)
    service = _service([_report(captured)], device)

    assert service.get_device_state(device.id).sections[0].is_stale is False


def test_staleness_uses_the_same_threshold_as_the_dashboard(device):
    captured = datetime.now(UTC) - timedelta(seconds=400)

    assert (
        _service([_report(captured)], device, stale_after_seconds=300)
        .get_device_state(device.id)
        .sections[0]
        .is_stale
        is True
    )
    assert (
        _service([_report(captured)], device, stale_after_seconds=900)
        .get_device_state(device.id)
        .sections[0]
        .is_stale
        is False
    )


def test_device_clock_running_ahead_clamps_to_zero(device):
    """A skewed device clock must not surface as a negative age."""
    captured = datetime.now(UTC) + timedelta(minutes=5)
    service = _service([_report(captured)], device)

    assert service.get_device_state(device.id).sections[0].age_seconds == 0


def test_naive_capture_timestamp_is_read_as_utc(device):
    """SQLite (and a stray naive write) hand back tz-less datetimes."""
    captured = (datetime.now(UTC) - timedelta(seconds=60)).replace(tzinfo=None)
    service = _service([_report(captured)], device)

    assert service.get_device_state(device.id).sections[0].age_seconds < 120


def test_device_that_never_reported_state_is_not_an_error(device):
    response = _service([], device).get_device_state(device.id)

    assert response.sections == []
    assert response.external_id == "WW-TEST-SN"


def test_org_scope_is_passed_through_to_the_device_lookup(device):
    repo = MagicMock()
    repo.list_latest_sections.return_value = []
    device_service = MagicMock()
    device_service.get_by_id.return_value = device
    settings = SimpleNamespace(telemetry_stale_after_seconds=300)
    service = DeviceStateQueryService(repo, device_service, settings)

    org_id = uuid4()
    service.get_device_state(device.id, organization_id=org_id)

    device_service.get_by_id.assert_called_once_with(device.id, organization_id=org_id)

"""Unit tests for the device state read channel on the ingest path (B-08).

The governing invariant across all of these: a state section is never allowed
to cost the packet its measurements. Whatever is wrong with a section, the
packet is still accepted and the windows still land.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.core_data.models.device import Device
from app.modules.telemetry.schemas.device_state import (
    MAX_SECTION_BYTES,
    MAX_SECTION_KEYS,
)
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    MeasurementPoint,
    MeasurementWindow,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService

CAPTURED_AT = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)

VALID_DEVICE_DATA = {
    "serial_number": "WW-TEST-SN",
    "firmware_version": "0.4.0",
    "registry_schema_version": 2,
    "uptime_seconds": 86400,
    "restart_count": 2,
    "restart_reason": "task_watchdog",
    "rssi_dbm": -67,
    "free_heap_bytes": 184320,
    "min_free_heap_bytes": 150000,
    "buffer_windows_used": 8,
    "buffer_windows_capacity": 48,
    "buffer_windows_dropped": 3,
}


def _packet(state: list[dict] | None = None) -> MeasurementPacketRequest:
    return MeasurementPacketRequest(
        v=2,
        device_id="WW-TEST-SN",
        seq=1,
        sent_at=CAPTURED_AT,
        windows=[
            MeasurementWindow(
                window_start=CAPTURED_AT,
                window_seconds=15,
                points=[
                    MeasurementPoint(
                        point_id="pt100_temperature",
                        type="temperature",
                        unit="°C",
                        quality="good",
                        value=21.5,
                    )
                ],
            )
        ],
        state=state or [],
    )


def _section(
    section: str = "device",
    schema_version: int = 1,
    data: dict | None = None,
) -> dict:
    return {
        "section": section,
        "schema_version": schema_version,
        "captured_at": CAPTURED_AT.isoformat(),
        "data": VALID_DEVICE_DATA if data is None else data,
    }


@pytest.fixture
def device() -> Device:
    dev = MagicMock(spec=Device)
    dev.id = uuid4()
    dev.external_id = "WW-TEST-SN"
    dev.water_object_id = uuid4()
    dev.is_active = True
    dev.firmware_version = None
    dev.last_seen_at = None
    dev.last_diagnostics_at = None
    return dev


@pytest.fixture
def state_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(state_repo: MagicMock) -> TelemetryIngestService:
    packet_repo = MagicMock()
    packet_repo.exists_by_device_seq.return_value = False
    packet_repo.create.return_value = MagicMock(id=uuid4())

    # Resolve the packet's point to a matching MeasurementPoint, so the only
    # error codes these tests observe are the ones the state channel raises.
    point_service = MagicMock()
    resolved_point = MagicMock()
    resolved_point.point_type = "temperature"
    resolved_point.unit = "°C"
    point_service.get_or_create_internal.return_value = resolved_point

    return TelemetryIngestService(
        packet_repository=packet_repo,
        point_service=point_service,
        state_repository=state_repo,
    )


def _stored_errors(service: TelemetryIngestService) -> list:
    """Error rows the service handed to the session, flattened."""
    add_all = service._packet_repository.session.add_all
    return [error for call in add_all.call_args_list for error in call.args[0]]


def test_valid_device_section_is_stored(service, state_repo, device):
    result = service.ingest(_packet([_section()]), device)

    assert result.status == "accepted"
    state_repo.create.assert_called_once()
    kwargs = state_repo.create.call_args.kwargs
    assert kwargs["section"] == "device"
    assert kwargs["schema_version"] == 1
    assert kwargs["captured_at"] == CAPTURED_AT
    assert kwargs["data"]["rssi_dbm"] == -67
    assert kwargs["device_id"] == "WW-TEST-SN"


def test_device_section_updates_device_denormalised_fields(service, device):
    service.ingest(_packet([_section()]), device)

    assert device.firmware_version == "0.4.0"
    assert device.last_diagnostics_at is not None
    assert device.last_seen_at == device.last_diagnostics_at


def test_packet_without_state_marks_contact_but_not_diagnostics(service, device):
    """The bug this channel fixes: 'last diagnostics' used to mean 'last seen'."""
    service.ingest(_packet(), device)

    assert device.last_seen_at is not None
    assert device.last_diagnostics_at is None


def test_retransmission_still_counts_as_contact(service, state_repo, device):
    """A duplicate carries no new data but still proves the device is alive."""
    service._packet_repository.exists_by_device_seq.return_value = True

    result = service.ingest(_packet([_section()]), device)

    assert result.status == "duplicate"
    assert device.last_seen_at is not None
    # The state already landed with the original packet; re-storing it would
    # violate the (packet_id, section) uniqueness the dedupe relies on.
    state_repo.create.assert_not_called()
    assert device.last_diagnostics_at is None


def test_unknown_section_is_flagged_and_dropped(service, state_repo, device):
    result = service.ingest(_packet([_section(section="wardrobe")]), device)

    assert result.status == "accepted"
    state_repo.create.assert_not_called()
    codes = [error.code for error in _stored_errors(service)]
    assert codes == ["STATE_SECTION_UNKNOWN"]


def test_schema_version_mismatch_is_flagged_but_stored(service, state_repo, device):
    """Forward compatibility: newer firmware still gets its state kept."""
    result = service.ingest(_packet([_section(schema_version=99)]), device)

    assert result.status == "accepted"
    state_repo.create.assert_called_once()
    assert state_repo.create.call_args.kwargs["schema_version"] == 99
    codes = [error.code for error in _stored_errors(service)]
    assert codes == ["STATE_SCHEMA_VERSION_MISMATCH"]


@pytest.mark.parametrize(
    "bad_data",
    [
        {**VALID_DEVICE_DATA, "restart_reason": "cosmic_rays"},
        {**VALID_DEVICE_DATA, "rssi_dbm": 500},
        {**VALID_DEVICE_DATA, "uptime_seconds": -1},
    ],
)
def test_malformed_section_is_flagged_but_stored(service, state_repo, device, bad_data):
    result = service.ingest(_packet([_section(data=bad_data)]), device)

    assert result.status == "accepted"
    state_repo.create.assert_called_once()
    codes = [error.code for error in _stored_errors(service)]
    assert codes == ["STATE_SECTION_INVALID"]


def test_unknown_field_in_section_passes_through(service, state_repo, device):
    """A field this backend has not learned about yet is kept, not dropped."""
    data = {**VALID_DEVICE_DATA, "modem_operator": "Plus"}

    service.ingest(_packet([_section(data=data)]), device)

    assert _stored_errors(service) == []
    assert state_repo.create.call_args.kwargs["data"]["modem_operator"] == "Plus"


def test_duplicate_section_in_one_packet_stores_only_the_first(
    service, state_repo, device
):
    packet = _packet([_section(), _section()])

    result = service.ingest(packet, device)

    assert result.status == "accepted"
    assert state_repo.create.call_count == 1
    codes = [error.code for error in _stored_errors(service)]
    assert codes == ["STATE_SECTION_INVALID"]


def test_state_is_optional_on_the_wire():
    """Firmware that reports no state stays a valid v2 client."""
    packet = MeasurementPacketRequest.model_validate(
        {
            "v": 2,
            "device_id": "WW-TEST-SN",
            "seq": 1,
            "sent_at": CAPTURED_AT.isoformat(),
            "windows": [
                {
                    "window_start": CAPTURED_AT.isoformat(),
                    "window_seconds": 15,
                    "points": [
                        {
                            "point_id": "p1",
                            "type": "temperature",
                            "unit": "°C",
                            "quality": "good",
                            "value": 1.0,
                        }
                    ],
                }
            ],
        }
    )

    assert packet.state == []


@pytest.mark.parametrize(
    "broken_section",
    [
        {**_section(), "surprise": 1},
        {k: v for k, v in _section().items() if k != "captured_at"},
        {**_section(), "schema_version": 0},
    ],
    ids=["extra-key", "no-captured-at", "zero-schema-version"],
)
def test_section_envelope_rejects_malformed_shapes(broken_section):
    """The envelope is strict even though section payloads are not."""
    with pytest.raises(ValueError):
        _packet([broken_section])


@pytest.mark.parametrize(
    "oversized",
    [
        {f"field_{i}": i for i in range(MAX_SECTION_KEYS + 1)},
        {"blob": "x" * (MAX_SECTION_BYTES + 1)},
    ],
    ids=["too-many-keys", "too-many-bytes"],
)
def test_section_payload_is_bounded(oversized):
    """`data` is stored verbatim, so its size has to be capped at the door."""
    with pytest.raises(ValueError):
        _packet([_section(data=oversized)])


def test_captured_at_is_the_device_clock_not_arrival(service, state_repo, device):
    """Freshness only works if capture time survives ingest untouched."""
    captured = datetime.now(UTC) - timedelta(minutes=20)
    section = _section()
    section["captured_at"] = captured.isoformat()

    service.ingest(_packet([section]), device)

    stored = state_repo.create.call_args.kwargs
    assert stored["captured_at"] == captured
    assert stored["received_at"] > stored["captured_at"]

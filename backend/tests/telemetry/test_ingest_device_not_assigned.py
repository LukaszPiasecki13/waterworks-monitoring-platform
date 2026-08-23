"""Tests for telemetry ingest guard on unassigned devices."""

import pytest

from app.core.errors import ConflictError
from app.modules.core_data.models.device import Device
from app.modules.telemetry.schemas.measurement_packet import MeasurementPacketRequest
from app.modules.telemetry.services.ingest import TelemetryIngestService


@pytest.mark.asyncio
async def test_ingest_device_not_assigned_raises_409(mocker):
    """Telemetry ingest raises 409 DEVICE_NOT_ASSIGNED when
    device.water_object_id is None."""
    repo = mocker.MagicMock()
    service = TelemetryIngestService(repo)

    # Create device with water_object_id = None (unassigned)
    device = mocker.MagicMock(spec=Device)
    device.external_id = "WW-TEST-SN"
    device.water_object_id = None
    device.is_active = True

    packet = MeasurementPacketRequest(
        device_id="WW-TEST-SN",
        seq=1,
        timestamp=mocker.MagicMock(),
        measurements=[],
    )

    with pytest.raises(ConflictError, match="DEVICE_NOT_ASSIGNED"):
        service.ingest(packet, device)


@pytest.mark.asyncio
async def test_ingest_device_assigned_succeeds(mocker):
    """Telemetry ingest succeeds when device.water_object_id is set."""
    repo = mocker.MagicMock()
    repo.exists_by_device_seq.return_value = False
    repo.transaction.return_value.__enter__ = mocker.MagicMock()
    repo.transaction.return_value.__exit__ = mocker.MagicMock(return_value=False)

    service = TelemetryIngestService(repo)

    # Create device WITH water_object_id (assigned)
    device = mocker.MagicMock(spec=Device)
    device.external_id = "WW-TEST-SN"
    device.water_object_id = "550e8400-e29b-41d4-a716-446655440000"  # Not None
    device.is_active = True

    packet = MeasurementPacketRequest(
        device_id="WW-TEST-SN",
        seq=1,
        timestamp=mocker.MagicMock(),
        measurements=[],
    )

    # Should not raise
    result = service.ingest(packet, device)
    assert result.status in ("accepted", "duplicate")

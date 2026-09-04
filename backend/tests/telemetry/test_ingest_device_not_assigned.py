"""Tests for telemetry ingest guard on unassigned devices."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError
from app.modules.core_data.models.device import Device
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    MeasurementPoint,
    MeasurementWindow,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService


def _packet(device_id: str, seq: int) -> MeasurementPacketRequest:
    return MeasurementPacketRequest(
        v=2,
        device_id=device_id,
        seq=seq,
        sent_at=datetime.now(UTC),
        windows=[
            MeasurementWindow(
                window_start=datetime.now(UTC),
                window_seconds=60,
                points=[
                    MeasurementPoint(
                        point_id="flow-1",
                        type="flow_rate",
                        unit="m³/h",
                        quality="good",
                        value=1.0,
                    )
                ],
            )
        ],
    )


@pytest.mark.asyncio
async def test_ingest_device_not_assigned_raises_409():
    """Telemetry ingest raises 409 DEVICE_NOT_ASSIGNED when
    device.water_object_id is None."""
    packet_repo = MagicMock()
    point_service = MagicMock()
    service = TelemetryIngestService(
        packet_repository=packet_repo,
        point_service=point_service,
        state_repository=MagicMock(),
    )

    # Create device with water_object_id = None (unassigned)
    device = MagicMock(spec=Device)
    device.external_id = "WW-TEST-SN"
    device.water_object_id = None
    device.is_active = True

    packet = _packet(device_id="WW-TEST-SN", seq=1)

    with pytest.raises(ConflictError) as exc_info:
        service.ingest(packet, device)
    assert exc_info.value.code == "DEVICE_NOT_ASSIGNED"


@pytest.mark.asyncio
async def test_ingest_device_assigned_succeeds():
    """Telemetry ingest succeeds when device.water_object_id is set."""
    packet_repo = MagicMock()
    point_service = MagicMock()
    packet_repo.exists_by_device_seq.return_value = False
    packet_repo.transaction.return_value.__enter__ = MagicMock()
    packet_repo.transaction.return_value.__exit__ = MagicMock(return_value=False)

    service = TelemetryIngestService(
        packet_repository=packet_repo,
        point_service=point_service,
        state_repository=MagicMock(),
    )

    # Create device WITH water_object_id (assigned)
    device = MagicMock(spec=Device)
    device.id = "550e8400-e29b-41d4-a716-446655440000"
    device.external_id = "WW-TEST-SN"
    device.water_object_id = "550e8400-e29b-41d4-a716-446655440001"  # Not None
    device.is_active = True

    packet = _packet(device_id="WW-TEST-SN", seq=1)

    # Should not raise
    result = service.ingest(packet, device)
    assert result.status in ("accepted", "duplicate")

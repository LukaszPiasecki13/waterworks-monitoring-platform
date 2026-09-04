"""Tests for telemetry ingest with device bearer token auth."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.errors import ForbiddenError
from app.modules.core_data.models.device import Device
from app.modules.telemetry.exceptions import TelemetryPacketAlreadyExistsError
from app.modules.telemetry.schemas.measurement_packet import (
    MeasurementPacketRequest,
    MeasurementPoint,
    MeasurementWindow,
)
from app.modules.telemetry.services.ingest import TelemetryIngestService


@pytest.fixture
def mock_packet_repository():
    return MagicMock()


@pytest.fixture
def mock_point_service():
    return MagicMock()


@pytest.fixture
def mock_state_repository():
    return MagicMock()


@pytest.fixture
def service(mock_packet_repository, mock_point_service, mock_state_repository):
    return TelemetryIngestService(
        packet_repository=mock_packet_repository,
        point_service=mock_point_service,
        state_repository=mock_state_repository,
    )


@pytest.fixture
def device():
    """Create a mock device for testing."""
    dev = MagicMock(spec=Device)
    dev.id = uuid4()
    dev.external_id = "TEST-SN-001"
    dev.water_object_id = uuid4()
    dev.is_active = True
    return dev


@pytest.fixture
def measurement_packet(device):
    """Create a measurement packet matching the device."""
    return MeasurementPacketRequest(
        v=2,
        device_id=device.external_id,
        seq=1,
        sent_at=datetime.now(UTC),
        windows=[
            MeasurementWindow(
                window_start=datetime.now(UTC),
                window_seconds=15,
                points=[
                    MeasurementPoint(
                        point_id="temp_01",
                        type="temperature",
                        unit="°C",
                        quality="good",
                        value=23.5,
                    )
                ],
            )
        ],
    )


def test_ingest_success(service, mock_packet_repository, device, measurement_packet):
    """Test successful telemetry ingest with device auth."""
    mock_packet_repository.exists_by_device_seq.return_value = False
    mock_packet_repository.create.return_value = MagicMock(id=uuid4())

    result = service.ingest(measurement_packet, device)

    assert result.status == "accepted"
    assert result.device_id == device.external_id
    assert result.seq == 1
    mock_packet_repository.create.assert_called_once()


def test_ingest_duplicate_packet(
    service, mock_packet_repository, device, measurement_packet
):
    """Test ingest returns duplicate status for already-ingested packet."""
    mock_packet_repository.exists_by_device_seq.return_value = True

    result = service.ingest(measurement_packet, device)

    assert result.status == "duplicate"
    assert result.device_id == device.external_id
    assert result.seq == 1
    mock_packet_repository.create.assert_not_called()


def test_ingest_device_id_mismatch(service, mock_packet_repository):
    """Test ingest fails when packet device_id doesn't match auth device."""
    device = MagicMock(spec=Device)
    device.id = uuid4()
    device.external_id = "DEVICE-A"
    device.is_active = True

    packet = MeasurementPacketRequest(
        v=2,
        device_id="DEVICE-B",  # Mismatch!
        seq=1,
        sent_at=datetime.now(UTC),
        windows=[
            MeasurementWindow(
                window_start=datetime.now(UTC),
                window_seconds=15,
                points=[
                    MeasurementPoint(
                        point_id="p1",
                        type="temperature",
                        unit="°C",
                        quality="good",
                        value=23.5,
                    )
                ],
            )
        ],
    )

    with pytest.raises(ForbiddenError) as exc_info:
        service.ingest(packet, device)

    assert "mismatch" in str(exc_info.value).lower()
    mock_packet_repository.create.assert_not_called()


def test_ingest_packet_already_exists_exception(
    service, mock_packet_repository, device, measurement_packet
):
    """Test ingest handles TelemetryPacketAlreadyExistsError from repo."""
    mock_packet_repository.exists_by_device_seq.return_value = False
    mock_packet_repository.create.side_effect = TelemetryPacketAlreadyExistsError(
        device_id=device.external_id, seq=1
    )

    result = service.ingest(measurement_packet, device)

    assert result.status == "duplicate"
    assert result.device_id == device.external_id


def test_ingest_uses_bearer_auth_device(
    service, mock_packet_repository, measurement_packet
):
    """Test that ingest uses the authenticated device from bearer token."""
    device = MagicMock(spec=Device)
    device.id = uuid4()
    device.external_id = "AUTH-DEVICE"
    device.water_object_id = uuid4()

    # Packet references the same device
    packet = MeasurementPacketRequest(
        v=2,
        device_id="AUTH-DEVICE",
        seq=42,
        sent_at=datetime.now(UTC),
        windows=[
            MeasurementWindow(
                window_start=datetime.now(UTC),
                window_seconds=15,
                points=[
                    MeasurementPoint(
                        point_id="p1",
                        type="temperature",
                        unit="°C",
                        quality="good",
                        value=99.9,
                    )
                ],
            )
        ],
    )

    mock_packet_repository.exists_by_device_seq.return_value = False

    result = service.ingest(packet, device)

    assert result.status == "accepted"
    assert result.seq == 42
    # Verify create was called with the packet data
    call_args = mock_packet_repository.create.call_args
    assert call_args is not None


def test_ingest_multiple_devices_isolation(service, mock_packet_repository):
    """Test that devices cannot ingest under each other's IDs."""
    device_a = MagicMock(spec=Device)
    device_a.external_id = "DEVICE-A"

    device_b = MagicMock(spec=Device)
    device_b.external_id = "DEVICE-B"

    packet_for_a = MeasurementPacketRequest(
        v=2,
        device_id="DEVICE-A",
        seq=1,
        sent_at=datetime.now(UTC),
        windows=[
            MeasurementWindow(
                window_start=datetime.now(UTC),
                window_seconds=15,
                points=[
                    MeasurementPoint(
                        point_id="p1",
                        type="temperature",
                        unit="°C",
                        quality="good",
                        value=1.0,
                    )
                ],
            )
        ],
    )

    # Device B tries to ingest under Device A's ID
    with pytest.raises(ForbiddenError):
        service.ingest(packet_for_a, device_b)

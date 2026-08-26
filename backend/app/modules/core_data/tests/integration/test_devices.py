"""Integration tests for device detach and complete deletion."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.errors import NotFoundError
from app.modules.core_data.models import (
    Device,
    MeasurementPoint,
    Organization,
    User,
    WaterObject,
)
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.services.device_lifecycle import DeviceLifecycleService
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.security.access import OrganizationAccess
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.services.ingest import TelemetryIngestService


def _setup_device_with_measurement_point(
    db_session: Session,
) -> tuple[Device, MeasurementPoint]:
    """Helper: create org, water object, credential, device, and measurement point."""
    org = Organization(id=uuid4(), name="OrgTest")
    db_session.add(org)
    db_session.flush()

    water_obj = WaterObject(
        id=uuid4(),
        organization_id=org.id,
        name="WaterObj",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(water_obj)
    db_session.flush()

    credential = DeviceCredential(
        id=uuid4(),
        serial_number="device-test-sn",
        public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
        status="claimed",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(credential)
    db_session.flush()

    device = Device(
        id=uuid4(),
        water_object_id=water_obj.id,
        external_id="device-test-sn",
        device_credential_id=credential.id,
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(device)
    db_session.flush()

    point = MeasurementPoint(
        id=uuid4(),
        device_id=device.id,
        external_id="point-1",
        point_type="pressure",
        unit="bar",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(point)
    db_session.commit()

    return device, point


def test_detach_from_organization_sets_water_object_to_none(
    db_session: Session,
) -> None:
    """Detach should set water_object_id to None but keep device in system."""
    device, _ = _setup_device_with_measurement_point(db_session)
    original_id = device.id
    org_id = device.water_object_id

    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = DeviceService(repo, water_obj_repo, MagicMock())

    admin = User(
        id=uuid4(),
        username="admin_detach",
        email="admin@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Test",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    water_obj = db_session.query(WaterObject).filter_by(id=org_id).one()
    db_session.commit()

    context = OrganizationAccess(
        actor=admin,
        organization_id=water_obj.organization_id,
        permissions={"CAN_MANAGE_ASSETS"},
    )

    result = service.detach_from_organization(original_id, context)

    assert result.id == original_id
    assert result.water_object_id is None
    assert result.device_credential_id is not None
    db_session.refresh(device)
    assert device.water_object_id is None


def test_detach_raises_not_found_if_device_not_in_org(
    db_session: Session,
) -> None:
    """Detach should raise NotFoundError if device not in org."""
    device, _ = _setup_device_with_measurement_point(db_session)

    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = DeviceService(repo, water_obj_repo, MagicMock())

    admin = User(
        id=uuid4(),
        username="admin_other_org",
        email="admin_other@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Test",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    other_org = Organization(id=uuid4(), name="OtherOrg")
    db_session.add(other_org)
    db_session.commit()

    context = OrganizationAccess(
        actor=admin,
        organization_id=other_org.id,
        permissions={"CAN_MANAGE_ASSETS"},
    )

    with pytest.raises(NotFoundError):
        service.detach_from_organization(device.id, context)


def test_device_deletion_cascades_measurement_points(
    db_session: Session,
) -> None:
    """Complete device deletion should cascade delete measurement_points via FK."""
    device, _ = _setup_device_with_measurement_point(db_session)

    # Verify measurement point exists
    mp_count = db_session.query(MeasurementPoint).filter_by(device_id=device.id).count()
    assert mp_count == 1

    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = DeviceService(repo, water_obj_repo, MagicMock())

    # Delete the device record (simulating what orchestrator does)
    service.delete_device_record(
        device.id,
        actor_id="platform-admin",
        actor_display_name="Platform Admin",
    )
    db_session.flush()

    # Verify measurement point was cascade-deleted
    mp_count = db_session.query(MeasurementPoint).filter_by(device_id=device.id).count()
    assert mp_count == 0


def test_complete_device_deletion_with_lifecycle_service(
    db_session: Session,
) -> None:
    """Complete deletion should remove device, credential, and telemetry."""
    device, _ = _setup_device_with_measurement_point(db_session)
    original_credential_id = device.device_credential_id
    original_external_id = device.external_id

    # Add telemetry packet for this device
    packet = TelemetryPacket(
        id=uuid4(),
        device_id=original_external_id,
        seq=1,
        sent_at=datetime(2026, 1, 1),
        received_at=datetime(2026, 1, 1),
        payload={"pressure": 1.5},
    )
    db_session.add(packet)
    db_session.commit()

    # Setup services
    device_repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    credential_repo = DeviceCredentialRepository(db_session)
    telemetry_packet_repo = TelemetryPacketRepository(db_session)
    point_repo = MeasurementPointRepository(db_session)
    device_service = DeviceService(device_repo, water_obj_repo, MagicMock())
    point_service = MeasurementPointService(point_repo, device_repo, MagicMock())
    telemetry_service = TelemetryIngestService(telemetry_packet_repo, point_service)
    audit_mock = MagicMock(spec=AuditPort)
    lifecycle_service = DeviceLifecycleService(
        device_service, credential_repo, telemetry_service, audit_mock
    )

    # Execute complete deletion
    lifecycle_service.delete_device_completely(
        device.id,
        actor_id="platform-admin",
        actor_display_name="Platform Admin",
    )
    db_session.commit()

    # Verify device is deleted
    device_count = db_session.query(Device).filter_by(id=device.id).count()
    assert device_count == 0

    # Verify credential is deleted
    credential_count = (
        db_session.query(DeviceCredential).filter_by(id=original_credential_id).count()
    )
    assert credential_count == 0

    # Verify telemetry is deleted
    packet_count = (
        db_session.query(TelemetryPacket)
        .filter_by(device_id=original_external_id)
        .count()
    )
    assert packet_count == 0

    # Verify audit was called (at least once for credential DELETE)
    assert audit_mock.record.call_count >= 1


def test_complete_deletion_raises_not_found_for_missing_device(
    db_session: Session,
) -> None:
    """DeviceLifecycleService should raise NotFoundError if device not found."""
    device_repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    credential_repo = DeviceCredentialRepository(db_session)
    telemetry_packet_repo = TelemetryPacketRepository(db_session)
    point_repo = MeasurementPointRepository(db_session)
    device_service = DeviceService(device_repo, water_obj_repo, MagicMock())
    point_service = MeasurementPointService(point_repo, device_repo, MagicMock())
    telemetry_service = TelemetryIngestService(telemetry_packet_repo, point_service)
    lifecycle_service = DeviceLifecycleService(
        device_service, credential_repo, telemetry_service, MagicMock()
    )

    with pytest.raises(NotFoundError):
        lifecycle_service.delete_device_completely(
            uuid4(),
            actor_id="platform-admin",
            actor_display_name="Platform Admin",
        )

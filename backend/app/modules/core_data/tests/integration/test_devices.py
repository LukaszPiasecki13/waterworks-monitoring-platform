from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.core_data.models import Device, Organization, User, WaterObject
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.device_identity.models.device_credential import DeviceCredential


def test_device_delete_with_measurement_points_raises_conflict_error(
    db_session: Session,
) -> None:
    """Deleting device with related measurement points should raise ConflictError."""
    from app.core.errors import ConflictError

    org = Organization(id=uuid4(), name="OrgDeleteTest")
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
        serial_number="device-delete-test",
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
        external_id="device-delete-test",
        device_credential_id=credential.id,
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(device)
    db_session.flush()

    # Add measurement point that references the device (FK constraint)
    from app.modules.core_data.models import MeasurementPoint

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

    # Try to delete device via service - should raise ConflictError
    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    from app.modules.core_data.services.devices import DeviceService

    service = DeviceService(repo, water_obj_repo, MagicMock())

    admin = User(
        id=uuid4(),
        username="admin_delete_test",
        email="admin_delete_test@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Test",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    import pytest

    from app.modules.security.access import OrganizationAccess

    context = OrganizationAccess(
        actor=admin,
        organization_id=org.id,
        permissions={"CAN_MANAGE_ASSETS"},
    )

    with pytest.raises(ConflictError):
        service.delete(device.id, context)

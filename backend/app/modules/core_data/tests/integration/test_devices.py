from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.core_data.models import Device, Organization, User, WaterObject
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.devices import ListDevicesRequest
from app.modules.core_data.services.devices import DeviceService


def test_admin_filtering_devices_by_organization_id_returns_only_that_org_devices(
    db_session: Session,
) -> None:
    # Setup
    org1 = Organization(id=uuid4(), name="Org1_DeviceTest")
    org2 = Organization(id=uuid4(), name="Org2_DeviceTest")
    db_session.add_all([org1, org2])
    db_session.flush()

    water_obj1 = WaterObject(
        id=uuid4(),
        organization_id=org1.id,
        name="WaterObj in Org1",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    water_obj2 = WaterObject(
        id=uuid4(),
        organization_id=org2.id,
        name="WaterObj in Org2",
        object_type="hydrophore",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([water_obj1, water_obj2])
    db_session.flush()

    device1 = Device(
        id=uuid4(),
        water_object_id=water_obj1.id,
        external_id="device-org1",
        hashed_secret="hash1",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    device2 = Device(
        id=uuid4(),
        water_object_id=water_obj2.id,
        external_id="device-org2",
        hashed_secret="hash2",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([device1, device2])

    admin = User(
        id=uuid4(),
        username="admin_device_test",
        email="admin_device_test@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Test",
        status="admin",
        is_active=True,
        organization_id=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    # Test filtering by organization_id
    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = DeviceService(repo, water_obj_repo, MagicMock())

    query = ListDevicesRequest(organization_id=org1.id)
    devices, count = service.list_all(query, actor=admin)

    assert count == 1
    assert len(devices) == 1
    assert devices[0].external_id == "device-org1"


def test_regular_user_ignores_organization_id_query_param_in_devices_list(
    db_session: Session,
) -> None:
    # Setup
    user_org = Organization(id=uuid4(), name="UserOrg_DeviceTest")
    other_org = Organization(id=uuid4(), name="OtherOrg_DeviceTest")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    user_water_obj = WaterObject(
        id=uuid4(),
        organization_id=user_org.id,
        name="User's WaterObj",
        object_type="intake",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_water_obj = WaterObject(
        id=uuid4(),
        organization_id=other_org.id,
        name="Other's WaterObj",
        object_type="network_point",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([user_water_obj, other_water_obj])
    db_session.flush()

    user_device = Device(
        id=uuid4(),
        water_object_id=user_water_obj.id,
        external_id="user-device",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_device = Device(
        id=uuid4(),
        water_object_id=other_water_obj.id,
        external_id="other-device",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([user_device, other_device])

    regular_user = User(
        id=uuid4(),
        username="user_device_test",
        email="user_device_test@example.com",
        hashed_password="hash",
        first_name="Regular",
        last_name="User",
        status="regular",
        is_active=True,
        organization_id=user_org.id,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(regular_user)
    db_session.commit()

    # Even requesting other_org, should only see own org
    repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = DeviceService(repo, water_obj_repo, MagicMock())

    query = ListDevicesRequest(organization_id=other_org.id)
    devices, count = service.list_all(query, actor=regular_user)

    assert count == 1
    assert len(devices) == 1
    assert devices[0].external_id == "user-device"


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

    device = Device(
        id=uuid4(),
        water_object_id=water_obj.id,
        external_id="device-delete-test",
        hashed_secret="hash",
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
        status="admin",
        is_active=True,
        organization_id=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    import pytest

    with pytest.raises(ConflictError):
        service.delete(device.id, actor=admin)

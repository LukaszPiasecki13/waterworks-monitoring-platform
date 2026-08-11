from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.core_data.models import Device, MeasurementPoint, Organization, User, WaterObject
from app.modules.core_data.repositories.measurement_points import MeasurementPointRepository
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.services.measurement_points import MeasurementPointService
from app.modules.core_data.schemas.measurement_points import ListMeasurementPointsRequest


def test_admin_filtering_measurement_points_by_organization_id(
    db_session: Session,
) -> None:
    # Setup
    org1 = Organization(id=uuid4(), name="Org1_PointTest")
    org2 = Organization(id=uuid4(), name="Org2_PointTest")
    db_session.add_all([org1, org2])
    db_session.flush()

    water_obj1 = WaterObject(
        id=uuid4(),
        organization_id=org1.id,
        name="WaterObj Org1",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    water_obj2 = WaterObject(
        id=uuid4(),
        organization_id=org2.id,
        name="WaterObj Org2",
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
        external_id="dev1",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    device2 = Device(
        id=uuid4(),
        water_object_id=water_obj2.id,
        external_id="dev2",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([device1, device2])
    db_session.flush()

    point1 = MeasurementPoint(
        id=uuid4(),
        device_id=device1.id,
        external_id="point1",
        point_type="pressure",
        unit="bar",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    point2 = MeasurementPoint(
        id=uuid4(),
        device_id=device2.id,
        external_id="point2",
        point_type="flow_rate",
        unit="l/min",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([point1, point2])

    admin = User(
        id=uuid4(),
        username="admin_point_test",
        email="admin_point_test@example.com",
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
    repo = MeasurementPointRepository(db_session)
    device_repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = MeasurementPointService(repo, device_repo, water_obj_repo, MagicMock())

    query = ListMeasurementPointsRequest(organization_id=org1.id)
    points, count = service.list_all(query, actor=admin)

    assert count == 1
    assert len(points) == 1
    assert points[0].external_id == "point1"


def test_regular_user_ignores_organization_id_query_param_in_measurement_points(
    db_session: Session,
) -> None:
    # Setup
    user_org = Organization(id=uuid4(), name="UserOrg_PointTest")
    other_org = Organization(id=uuid4(), name="OtherOrg_PointTest")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    user_water_obj = WaterObject(
        id=uuid4(),
        organization_id=user_org.id,
        name="User WaterObj",
        object_type="intake",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_water_obj = WaterObject(
        id=uuid4(),
        organization_id=other_org.id,
        name="Other WaterObj",
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
        external_id="user_dev",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_device = Device(
        id=uuid4(),
        water_object_id=other_water_obj.id,
        external_id="other_dev",
        hashed_secret="hash",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([user_device, other_device])
    db_session.flush()

    user_point = MeasurementPoint(
        id=uuid4(),
        device_id=user_device.id,
        external_id="user_point",
        point_type="pressure",
        unit="bar",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_point = MeasurementPoint(
        id=uuid4(),
        device_id=other_device.id,
        external_id="other_point",
        point_type="flow_rate",
        unit="l/min",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([user_point, other_point])

    regular_user = User(
        id=uuid4(),
        username="user_point_test",
        email="user_point_test@example.com",
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
    repo = MeasurementPointRepository(db_session)
    device_repo = DeviceRepository(db_session)
    water_obj_repo = WaterObjectRepository(db_session)
    service = MeasurementPointService(repo, device_repo, water_obj_repo, MagicMock())

    query = ListMeasurementPointsRequest(organization_id=other_org.id)
    points, count = service.list_all(query, actor=regular_user)

    assert count == 1
    assert len(points) == 1
    assert points[0].external_id == "user_point"

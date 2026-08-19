"""Tests for cross-organization isolation and access control boundaries.

Verifies that org-scoped permissions create impenetrable boundaries:
- Users cannot access resources outside their organization
- List operations filter by membership automatically
- Org-scoped permissions prevent cross-org privilege escalation
"""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.core_data.models import (
    Device,
    Organization,
    User,
    WaterObject,
)
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.devices import (
    DeviceUpdateRequest,
    ListDevicesRequest,
)
from app.modules.core_data.schemas.measurement_points import (
    ListMeasurementPointsRequest,
    MeasurementPointUpdateRequest,
)
from app.modules.core_data.schemas.water_objects import (
    ListWaterObjectsRequest,
    WaterObjectUpdateRequest,
)
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.security.access import OrganizationAccess


@pytest.fixture
def org_a_and_b(db_session: Session):
    """Create two separate organizations with resources."""
    org_a = Organization(id=uuid4(), name="OrgA")
    org_b = Organization(id=uuid4(), name="OrgB")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Create water objects in each org
    water_a = WaterObject(
        id=uuid4(),
        organization_id=org_a.id,
        name="Water A",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    water_b = WaterObject(
        id=uuid4(),
        organization_id=org_b.id,
        name="Water B",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([water_a, water_b])
    db_session.flush()

    # Create devices in each org
    device_a = Device(
        id=uuid4(),
        water_object_id=water_a.id,
        external_id="device-a",
        hashed_secret="hash-a",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    device_b = Device(
        id=uuid4(),
        water_object_id=water_b.id,
        external_id="device-b",
        hashed_secret="hash-b",
        firmware_version="1.0",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([device_a, device_b])
    db_session.commit()

    return {
        "org_a": org_a,
        "org_b": org_b,
        "water_a": water_a,
        "water_b": water_b,
        "device_a": device_a,
        "device_b": device_b,
    }


@pytest.fixture
def user_org_a(db_session: Session, org_a_and_b):
    """Create a user belonging to org A only."""
    from app.modules.core_data.repositories.users_organizations import (
        UsersOrganizationsRepository,
    )

    user = User(
        id=uuid4(),
        username="user_a",
        email="user_a@example.com",
        hashed_password="hash",
        first_name="User",
        last_name="A",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(user)
    db_session.flush()

    # Add user to org A
    members_repo = UsersOrganizationsRepository(db_session)
    members_repo.add_member(user.id, org_a_and_b["org_a"].id)
    db_session.commit()

    return user


@pytest.fixture
def user_org_b(db_session: Session, org_a_and_b):
    """Create a user belonging to org B only."""
    from app.modules.core_data.repositories.users_organizations import (
        UsersOrganizationsRepository,
    )

    user = User(
        id=uuid4(),
        username="user_b",
        email="user_b@example.com",
        hashed_password="hash",
        first_name="User",
        last_name="B",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(user)
    db_session.flush()

    # Add user to org B
    members_repo = UsersOrganizationsRepository(db_session)
    members_repo.add_member(user.id, org_a_and_b["org_b"].id)
    db_session.commit()

    return user


class TestDevicesCrossOrgIsolation:
    """Verify devices cannot be accessed across org boundaries."""

    def test_user_org_a_cannot_get_device_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to GET device from org B."""
        repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        service = DeviceService(repo, water_obj_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        # Attempt to access device from org B using org A context
        with pytest.raises(NotFoundError):
            service.get_by_id(org_a_and_b["device_b"].id, context)

    def test_user_org_a_cannot_update_device_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to PATCH device from org B."""
        repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        service = DeviceService(repo, water_obj_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        request = DeviceUpdateRequest(is_active=False)

        # Attempt to update device from org B using org A context
        with pytest.raises(NotFoundError):
            service.update(org_a_and_b["device_b"].id, request, context)

    def test_user_org_a_cannot_delete_device_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to DELETE device from org B."""
        repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        service = DeviceService(repo, water_obj_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        # Attempt to delete device from org B using org A context
        with pytest.raises(NotFoundError):
            service.delete(org_a_and_b["device_b"].id, context)

    def test_list_devices_filters_by_membership(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """List devices should filter by organization membership."""
        repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        service = DeviceService(repo, water_obj_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        query = ListDevicesRequest(skip=0, limit=100)
        devices, total = service.list_all(query, context)

        # Should only see device from org A, not org B
        assert total == 1
        assert len(devices) == 1
        assert devices[0].id == org_a_and_b["device_a"].id


class TestWaterObjectsCrossOrgIsolation:
    """Verify water objects cannot be accessed across org boundaries."""

    def test_user_org_a_cannot_get_water_object_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to GET water object from org B."""
        repo = WaterObjectRepository(db_session)
        org_repo = OrganizationRepository(db_session)
        service = WaterObjectService(repo, org_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        # Attempt to access water object from org B using org A context
        with pytest.raises(NotFoundError):
            service.get_by_id(org_a_and_b["water_b"].id, context)

    def test_user_org_a_cannot_update_water_object_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to PATCH water object from org B."""
        repo = WaterObjectRepository(db_session)
        org_repo = OrganizationRepository(db_session)
        service = WaterObjectService(repo, org_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        request = WaterObjectUpdateRequest(name="New Name")

        # Attempt to update water object from org B using org A context
        with pytest.raises(NotFoundError):
            service.update(org_a_and_b["water_b"].id, request, context)

    def test_user_org_a_cannot_delete_water_object_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to DELETE water object from org B."""
        repo = WaterObjectRepository(db_session)
        org_repo = OrganizationRepository(db_session)
        service = WaterObjectService(repo, org_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        # Attempt to delete water object from org B using org A context
        with pytest.raises(NotFoundError):
            service.delete(org_a_and_b["water_b"].id, context)

    def test_list_water_objects_filters_by_membership(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """List water objects should filter by organization membership."""
        repo = WaterObjectRepository(db_session)
        org_repo = OrganizationRepository(db_session)
        service = WaterObjectService(repo, org_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        query = ListWaterObjectsRequest(skip=0, limit=100)
        objs, total = service.list_all(query, context)

        # Should only see water object from org A, not org B
        assert total == 1
        assert len(objs) == 1
        assert objs[0].id == org_a_and_b["water_a"].id


class TestMeasurementPointsCrossOrgIsolation:
    """Verify measurement points cannot be accessed across org boundaries."""

    def _create_measurement_point(self, db_session: Session, device_id):
        """Helper to create a measurement point for a device."""
        from app.modules.core_data.models import MeasurementPoint

        point = MeasurementPoint(
            id=uuid4(),
            device_id=device_id,
            external_id=f"point-{uuid4().hex[:8]}",
            point_type="pressure",
            unit="bar",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(point)
        db_session.commit()
        return point

    def test_user_org_a_cannot_get_measurement_point_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to GET measurement point from org B."""
        # Create a measurement point in org B's device
        point_b = self._create_measurement_point(db_session, org_a_and_b["device_b"].id)

        repo = MeasurementPointRepository(db_session)
        device_repo = DeviceRepository(db_session)
        service = MeasurementPointService(repo, device_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        # Attempt to access measurement point from org B using org A context
        with pytest.raises(NotFoundError):
            service.get_by_id(point_b.id, context)

    def test_user_org_a_cannot_update_measurement_point_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to PATCH measurement point from org B."""
        point_b = self._create_measurement_point(db_session, org_a_and_b["device_b"].id)

        repo = MeasurementPointRepository(db_session)
        device_repo = DeviceRepository(db_session)
        service = MeasurementPointService(repo, device_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        request = MeasurementPointUpdateRequest(is_active=False)

        # Attempt to update measurement point from org B using org A context
        with pytest.raises(NotFoundError):
            service.update(point_b.id, request, context)

    def test_user_org_a_cannot_delete_measurement_point_from_org_b(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """User in org A should not be able to DELETE measurement point from org B."""
        point_b = self._create_measurement_point(db_session, org_a_and_b["device_b"].id)

        repo = MeasurementPointRepository(db_session)
        device_repo = DeviceRepository(db_session)
        service = MeasurementPointService(repo, device_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        # Attempt to delete measurement point from org B using org A context
        with pytest.raises(NotFoundError):
            service.delete(point_b.id, context)

    def test_list_measurement_points_filters_by_membership(
        self, db_session: Session, org_a_and_b, user_org_a
    ):
        """List measurement points should filter by organization membership."""
        # Create measurement points in both orgs
        point_a = self._create_measurement_point(db_session, org_a_and_b["device_a"].id)
        self._create_measurement_point(db_session, org_a_and_b["device_b"].id)

        repo = MeasurementPointRepository(db_session)
        device_repo = DeviceRepository(db_session)
        service = MeasurementPointService(repo, device_repo, MagicMock())

        context = OrganizationAccess(
            actor=user_org_a,
            organization_id=org_a_and_b["org_a"].id,
            permissions={"CAN_VIEW_ASSETS"},
        )

        query = ListMeasurementPointsRequest(skip=0, limit=100, device_id=None)
        points, total = service.list_all(query, context)

        # Should only see measurement point from org A, not org B
        assert total == 1
        assert len(points) == 1
        assert points[0].id == point_a.id

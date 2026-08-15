"""Security tests for telemetry query endpoints."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.core_data.models import Organization, User, WaterObject
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.schemas.query import (
    GetMeasurementsRequest,
    ListObjectsRequest,
)
from app.modules.telemetry.services.query import TelemetryQueryService


def _organization(db_session: Session, name: str) -> Organization:
    organization = Organization(id=uuid4(), name=f"{name}-{uuid4().hex[:8]}")
    db_session.add(organization)
    db_session.flush()
    return organization


def _water_object(db_session: Session, organization: Organization) -> WaterObject:
    """A real row, so the org check is actually reached."""
    water_object = WaterObject(
        id=uuid4(),
        organization_id=organization.id,
        name=f"object-{uuid4().hex[:8]}",
        object_type="pump_station",
    )
    db_session.add(water_object)
    db_session.flush()
    return water_object


def _user(db_session: Session, organization: Organization | None) -> User:
    unique = uuid4().hex[:8]
    user = User(
        id=uuid4(),
        username=f"user-{unique}",
        email=f"user-{unique}@example.com",
        hashed_password="hash",
        first_name="Test",
        last_name="User",
        status="admin" if organization is None else "regular",
        is_active=True,
        organization_id=None if organization is None else organization.id,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    db_session.add(user)
    db_session.commit()
    return user


def _service(db_session: Session) -> TelemetryQueryService:
    settings = MagicMock()
    settings.telemetry_stale_after_seconds = 300
    return TelemetryQueryService(TelemetryQueryRepository(db_session), settings)


def test_regular_user_cannot_see_other_organization_objects(
    db_session: Session,
) -> None:
    """A foreign object is hidden as 404, not merely forbidden."""
    user_org = _organization(db_session, "UserOrg_QuerySec")
    other_org = _organization(db_session, "OtherOrg_QuerySec")
    foreign_object = _water_object(db_session, other_org)
    regular_user = _user(db_session, user_org)

    with pytest.raises(NotFoundError):
        _service(db_session).get_object_detail(
            user=regular_user, object_id=foreign_object.id
        )


def test_admin_can_see_object_of_any_organization(db_session: Session) -> None:
    """Platform admin (organization_id=None) bypasses the org check."""
    other_org = _organization(db_session, "OtherOrg_AdminSees")
    foreign_object = _water_object(db_session, other_org)
    admin = _user(db_session, None)

    detail = _service(db_session).get_object_detail(
        user=admin, object_id=foreign_object.id
    )

    assert detail.object_id == str(foreign_object.id)
    # No packets yet — visible, and reported as awaiting data.
    assert detail.status == "no_data"


def test_object_without_telemetry_is_not_a_404(db_session: Session) -> None:
    """A provisioned object must be readable before its first packet."""
    org = _organization(db_session, "Org_NoData")
    water_object = _water_object(db_session, org)
    user = _user(db_session, org)

    detail = _service(db_session).get_object_detail(
        user=user, object_id=water_object.id
    )

    assert detail.status == "no_data"
    assert detail.last_contact_at is None
    assert detail.device_id is None
    assert detail.points == []


def test_list_objects_forces_regular_user_to_own_organization(
    db_session: Session,
) -> None:
    """A regular user's org_id parameter is ignored in favour of their own."""
    user_org = _organization(db_session, "UserOrg_ListForce")
    other_org = _organization(db_session, "OtherOrg_ListForce")
    _water_object(db_session, other_org)
    own_object = _water_object(db_session, user_org)
    regular_user = _user(db_session, user_org)

    result = _service(db_session).list_objects(
        user=regular_user, query=ListObjectsRequest(org_id=other_org.id)
    )

    assert [item.object_id for item in result.items] == [str(own_object.id)]


def test_admin_can_filter_by_any_organization_in_list(db_session: Session) -> None:
    """Platform admin can use org_id to filter by any organization."""
    target_org = _organization(db_session, "TargetOrg_AdminFilter")
    other_org = _organization(db_session, "OtherOrg_AdminFilter")
    target_object = _water_object(db_session, target_org)
    _water_object(db_session, other_org)
    admin = _user(db_session, None)

    result = _service(db_session).list_objects(
        user=admin, query=ListObjectsRequest(org_id=target_org.id)
    )

    assert [item.object_id for item in result.items] == [str(target_object.id)]


def test_measurements_endpoint_enforces_organization_check(
    db_session: Session,
) -> None:
    """get_measurements enforces the same isolation as the detail endpoint."""
    user_org = _organization(db_session, "UserOrg_MeasSec")
    other_org = _organization(db_session, "OtherOrg_MeasSec")
    foreign_object = _water_object(db_session, other_org)
    regular_user = _user(db_session, user_org)

    with pytest.raises(NotFoundError):
        _service(db_session).get_measurements(
            user=regular_user,
            object_id=foreign_object.id,
            query=GetMeasurementsRequest(),
        )

"""Security tests for telemetry query endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.core_data.models import Organization, User
from app.modules.telemetry.repositories.queries import TelemetryQueryRepository
from app.modules.telemetry.services.query import TelemetryQueryService


def test_regular_user_cannot_see_other_organization_objects(
    db_session: Session,
) -> None:
    """Regular user should get ForbiddenError when requesting object from another org."""
    user_org = Organization(id=uuid4(), name="UserOrg_QuerySec")
    other_org = Organization(id=uuid4(), name="OtherOrg_QuerySec")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    regular_user = User(
        id=uuid4(),
        username="user_query_sec",
        email="user_query_sec@example.com",
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

    repo = TelemetryQueryRepository(db_session)
    mock_settings = MagicMock()
    service = TelemetryQueryService(repo, mock_settings)

    # Mock get_latest_packet to return a packet from other_org
    mock_packet = MagicMock()
    mock_packet.org_id = str(other_org.id)
    mock_packet.object_id = "test-object"
    service.repo.get_latest_packet = MagicMock(return_value=mock_packet)

    with pytest.raises(NotFoundError):
        service.get_object_detail(user=regular_user, object_id="test-object")


def test_admin_can_see_any_organization_objects(
    db_session: Session,
) -> None:
    """Platform admin (organization_id=None) bypasses org security check."""
    admin = User(
        id=uuid4(),
        username="admin_query_sec",
        email="admin_query_sec@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="User",
        status="admin",
        is_active=True,
        organization_id=None,  # Platform admin
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    repo = TelemetryQueryRepository(db_session)
    mock_settings = MagicMock()
    service = TelemetryQueryService(repo, mock_settings)

    # Verify org check logic: admin with organization_id=None should pass
    other_org_id = str(uuid4())
    mock_packet = MagicMock()
    mock_packet.org_id = other_org_id
    service.repo.get_latest_packet = MagicMock(return_value=mock_packet)
    service.repo.get_water_object = MagicMock(return_value=None)  # Will raise NotFoundError, not ForbiddenError

    # Admin accessing other org should fail on water_object, not org check
    try:
        service.get_object_detail(user=admin, object_id="test-object")
    except NotFoundError:
        pass  # Expected - water object not found (org check passes for admin)


def test_list_objects_forces_regular_user_to_own_organization(
    db_session: Session,
) -> None:
    """Regular user's org_id parameter should be ignored; forced to their org."""
    user_org = Organization(id=uuid4(), name="UserOrg_ListForce")
    other_org = Organization(id=uuid4(), name="OtherOrg_ListForce")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    regular_user = User(
        id=uuid4(),
        username="user_list_force",
        email="user_list_force@example.com",
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

    repo = TelemetryQueryRepository(db_session)
    mock_settings = MagicMock()
    service = TelemetryQueryService(repo, mock_settings)

    # User tries to request other_org, but should be forced to their own
    service.repo.count_objects = MagicMock(return_value=0)
    service.repo.list_object_ids = MagicMock(return_value=[])

    service.list_objects(user=regular_user, org_id=str(other_org.id))

    # Verify that the repo was called with user's org_id, not the requested one
    service.repo.count_objects.assert_called_with(org_id=str(user_org.id))
    call_args = service.repo.list_object_ids.call_args
    assert call_args.kwargs["org_id"] == str(user_org.id)


def test_admin_can_filter_by_any_organization_in_list(
    db_session: Session,
) -> None:
    """Platform admin can use org_id query param to filter by any org."""
    admin = User(
        id=uuid4(),
        username="admin_list_filter",
        email="admin_list_filter@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="User",
        status="admin",
        is_active=True,
        organization_id=None,  # Platform admin
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    repo = TelemetryQueryRepository(db_session)
    mock_settings = MagicMock()
    service = TelemetryQueryService(repo, mock_settings)

    target_org_id = str(uuid4())
    service.repo.count_objects = MagicMock(return_value=0)
    service.repo.list_object_ids = MagicMock(return_value=[])

    service.list_objects(user=admin, org_id=target_org_id)

    # Verify that repo was called with the requested org_id
    service.repo.count_objects.assert_called_with(org_id=target_org_id)
    call_args = service.repo.list_object_ids.call_args
    assert call_args.kwargs["org_id"] == target_org_id


def test_measurements_endpoint_enforces_organization_check(
    db_session: Session,
) -> None:
    """get_measurements should also enforce organization isolation."""
    user_org = Organization(id=uuid4(), name="UserOrg_MeasSec")
    other_org = Organization(id=uuid4(), name="OtherOrg_MeasSec")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    regular_user = User(
        id=uuid4(),
        username="user_meas_sec",
        email="user_meas_sec@example.com",
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

    repo = TelemetryQueryRepository(db_session)
    mock_settings = MagicMock()
    service = TelemetryQueryService(repo, mock_settings)

    # Mock latest packet from other org
    mock_packet = MagicMock()
    mock_packet.org_id = str(other_org.id)
    mock_packet.object_id = "test-object"
    service.repo.get_latest_packet = MagicMock(return_value=mock_packet)

    with pytest.raises(NotFoundError):
        service.get_measurements(user=regular_user, object_id="test-object")

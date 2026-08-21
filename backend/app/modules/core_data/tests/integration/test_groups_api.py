"""Integration tests for platform and organization groups API endpoints.

These tests validate the new platform_groups and org_groups endpoints
introduced in Phase 8 (implementation) of the groups & permissions feature.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.api.org_groups import router as org_groups_router
from app.modules.core_data.api.platform_groups import router as platform_groups_router
from app.modules.core_data.models import Organization, User
from app.modules.security.dependencies import get_current_user
from app.modules.security.models import UserGroup


@pytest.fixture
def groups_api_client(db_session: Session, admin_user: User):
    """Test client with platform and org groups routers mounted."""
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(platform_groups_router, prefix="/api/v1/platform")
    app.include_router(org_groups_router, prefix="/api/v1")

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_platform_groups_create_success(
    groups_api_client: TestClient, db_session: Session
) -> None:
    """POST /api/v1/platform/groups creates platform-scoped group."""
    response = groups_api_client.post(
        "/api/v1/platform/groups",
        json={
            "name": f"Platform Editors {uuid4().hex[:8]}",
            "description": "Platform-level content editors",
            "permission_codes": ["PLATFORM_VIEW_ORGANIZATIONS"],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["description"] == "Platform-level content editors"
    assert {p["code"] for p in payload["permissions"]} == {
        "PLATFORM_VIEW_ORGANIZATIONS"
    }
    assert payload["organization_id"] is None, (
        "Platform group should have organization_id = None"
    )

    # Verify it's platform-scoped (organization_id is NULL) in the database
    group_id = payload["id"]
    group = db_session.query(UserGroup).filter(UserGroup.id == group_id).first()
    assert group.organization_id is None


def test_platform_groups_create_duplicate_returns_409(
    groups_api_client: TestClient, db_session: Session
) -> None:
    """POST /api/v1/platform/groups with duplicate name returns 409."""
    group_name = f"TestEditors{uuid4().hex[:8]}"

    # Create first group
    response1 = groups_api_client.post(
        "/api/v1/platform/groups",
        json={
            "name": group_name,
            "description": "First",
            "permission_codes": [],
        },
    )
    assert response1.status_code == 201

    # Try duplicate name
    response2 = groups_api_client.post(
        "/api/v1/platform/groups",
        json={
            "name": group_name,
            "description": "Second",
            "permission_codes": [],
        },
    )

    assert response2.status_code == 409


def test_platform_groups_delete_success(
    groups_api_client: TestClient, db_session: Session
) -> None:
    """DELETE /api/v1/platform/groups/{id} removes the group."""
    # Create a group
    group_name = f"TempGroup{uuid4().hex[:8]}"
    create_resp = groups_api_client.post(
        "/api/v1/platform/groups",
        json={
            "name": group_name,
            "description": "",
            "permission_codes": [],
        },
    )
    assert create_resp.status_code == 201
    group_id = create_resp.json()["id"]

    # Delete it
    delete_resp = groups_api_client.delete(f"/api/v1/platform/groups/{group_id}")

    assert delete_resp.status_code == 204

    # Verify it's gone from database
    group = db_session.query(UserGroup).filter(UserGroup.id == group_id).first()
    assert group is None


def test_org_groups_create_success(
    groups_api_client: TestClient, db_session: Session, admin_user: User
) -> None:
    """POST /api/v1/orgs/{org_id}/groups creates org-scoped group."""
    # Create org and add admin_user as member
    org = Organization(name=f"TestOrg{uuid4().hex[:8]}")
    db_session.add(org)
    db_session.flush()

    # Add admin_user to org
    from app.modules.core_data.models import UsersOrganizations

    db_session.add(UsersOrganizations(user_id=admin_user.id, organization_id=org.id))
    db_session.commit()

    response = groups_api_client.post(
        f"/api/v1/orgs/{org.id}/groups",
        json={
            "name": f"OrgEditors{uuid4().hex[:8]}",
            "description": "Organization editors",
            "permission_codes": ["CAN_VIEW_USERS"],
        },
    )

    assert response.status_code == 201
    payload = response.json()

    # Verify it's org-scoped (not platform-scoped) in the database
    group_id = payload["id"]
    group = db_session.query(UserGroup).filter(UserGroup.id == group_id).first()
    assert group.organization_id == org.id


def test_org_groups_same_name_different_org_succeeds(
    groups_api_client: TestClient, db_session: Session, admin_user: User
) -> None:
    """POST /api/v1/orgs/{org_id}/groups with name existing in different org
    succeeds (regression test for bug 7.1b)."""
    # Create two orgs and add admin_user as member
    org_a = Organization(name=f"OrgA{uuid4().hex[:8]}")
    org_b = Organization(name=f"OrgB{uuid4().hex[:8]}")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Add admin_user to both orgs
    from app.modules.core_data.models import UsersOrganizations

    db_session.add_all(
        [
            UsersOrganizations(user_id=admin_user.id, organization_id=org_a.id),
            UsersOrganizations(user_id=admin_user.id, organization_id=org_b.id),
        ]
    )
    db_session.commit()

    group_name = f"Operators{uuid4().hex[:8]}"

    # Create group in org_a
    response_a = groups_api_client.post(
        f"/api/v1/orgs/{org_a.id}/groups",
        json={
            "name": group_name,
            "description": "",
            "permission_codes": [],
        },
    )
    assert response_a.status_code == 201

    # Create group with same name in org_b - should succeed
    response_b = groups_api_client.post(
        f"/api/v1/orgs/{org_b.id}/groups",
        json={
            "name": group_name,
            "description": "",
            "permission_codes": [],
        },
    )

    assert response_b.status_code == 201
    # Verify group B is in org_b (not org_a)
    group_b_id = response_b.json()["id"]
    group_b = db_session.query(UserGroup).filter(UserGroup.id == group_b_id).first()
    assert group_b.organization_id == org_b.id


def test_org_groups_idor_put_returns_404(
    groups_api_client: TestClient, db_session: Session
) -> None:
    """PUT /api/v1/orgs/{org_a_id}/groups/{group_from_org_b_id} returns 404.

    Regression test for IDOR vulnerability: admin should not be able
    to modify groups belonging to a different org using org_a's endpoint.
    """
    # Create two orgs
    org_a = Organization(name=f"OrgA{uuid4().hex[:8]}")
    org_b = Organization(name=f"OrgB{uuid4().hex[:8]}")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Create a group in org_b (without admin access to org_b)
    from app.modules.security.repositories import PermissionRepository

    repo = PermissionRepository(db_session)
    group_b = repo.create_group(
        name=f"OrgBGroup{uuid4().hex[:8]}",
        description="In org B",
        organization_id=org_b.id,
    )
    db_session.commit()

    # Attempt IDOR: try to edit org_b's group via org_a's endpoint
    # (admin_user has admin access to everything, but we're testing the
    # URL protection: /orgs/{org_a_id}/groups/{group_id_from_org_b})
    response = groups_api_client.put(
        f"/api/v1/orgs/{org_a.id}/groups/{group_b.id}",
        json={
            "name": "Changed",
            "description": "Hacked",
            "permission_codes": [],
            "user_ids": [],
        },
    )

    # Should be 404 (not found in org_a), not 200 or 403
    assert response.status_code == 404


def test_org_groups_idor_delete_returns_404(
    groups_api_client: TestClient, db_session: Session
) -> None:
    """DELETE /api/v1/orgs/{org_a_id}/groups/{group_from_org_b_id} returns 404.

    Regression test for IDOR vulnerability.
    """
    # Create two orgs
    org_a = Organization(name=f"OrgA{uuid4().hex[:8]}")
    org_b = Organization(name=f"OrgB{uuid4().hex[:8]}")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Create a group in org_b
    from app.modules.security.repositories import PermissionRepository

    repo = PermissionRepository(db_session)
    group_b = repo.create_group(
        name=f"OrgBGroup{uuid4().hex[:8]}",
        description="In org B",
        organization_id=org_b.id,
    )
    db_session.commit()

    # Attempt IDOR: try to delete org_b's group via org_a's endpoint
    response = groups_api_client.delete(f"/api/v1/orgs/{org_a.id}/groups/{group_b.id}")

    # Should be 404
    assert response.status_code == 404

    # Verify group_b still exists in database
    group = db_session.query(UserGroup).filter(UserGroup.id == group_b.id).first()
    assert group is not None
    assert group.organization_id == org_b.id

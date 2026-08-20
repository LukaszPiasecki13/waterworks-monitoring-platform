from collections.abc import Generator
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.api.users import router as users_router
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.users import UserRepository
from app.modules.core_data.repositories.users_organizations import (
    UsersOrganizationsRepository,
)
from app.modules.security.dependencies import get_current_user
from app.modules.security.models import UserGroup, security_user_groups
from app.modules.security.permission_catalog import PLATFORM_VIEW_USERS
from app.modules.security.repositories import PermissionRepository


def test_user_repository_filters_and_counts_users(db_session: Session) -> None:
    repo = UserRepository(db_session)
    repo.create(
        username="anna",
        email="anna@example.com",
        hashed_password="hash",
        first_name="Anna",
        last_name="Nowak",
        is_active=True,
    )
    repo.create(
        username="jan",
        email="jan@example.com",
        hashed_password="hash",
        first_name="Jan",
        last_name="Kowalski",
        is_active=False,
    )
    db_session.commit()

    active_users = repo.list_all(search="anna", is_active=True)
    inactive_count = repo.count(is_active=False)

    assert [user.username for user in active_users] == ["anna"]
    assert inactive_count == 1
    assert repo.get_by_email("jan@example.com") is not None
    assert repo.get_by_username("missing") is None


def test_users_api_supports_admin_crud_flow(api_client) -> None:
    create_response = api_client.post(
        "/api/v1/users",
        json={
            "username": "PanelUser",
            "email": "panel@example.com",
            "password": "StrongPass123",
            "first_name": "Panel",
            "last_name": "User",
            "is_active": True,
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["username"] == "paneluser"

    list_response = api_client.get("/api/v1/users", params={"search": "panel"})
    assert list_response.status_code == 200
    assert [user["email"] for user in list_response.json()["items"]] == [
        "panel@example.com"
    ]

    update_response = api_client.patch(
        f"/api/v1/users/{created['id']}",
        json={"email": "updated@example.com"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["email"] == "updated@example.com"

    delete_response = api_client.delete(f"/api/v1/users/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "User deleted successfully"}

    missing_response = api_client.get(f"/api/v1/users/{created['id']}")
    assert missing_response.status_code == 404


def test_users_api_rejects_non_admin_user(db_session: Session) -> None:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session]:
        yield db_session

    mock_user_id = uuid4()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=mock_user_id,
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/users")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_security_group_viewer_can_list_users_for_membership_management(
    db_session: Session,
) -> None:
    user = UserRepository(db_session).create(
        username="security-viewer",
        email="security-viewer@example.com",
        hashed_password="hash",
        is_active=True,
    )
    repo = PermissionRepository(db_session)
    permission = repo.get_permission_by_code(PLATFORM_VIEW_USERS)
    if not permission:
        permission = repo.create_permission(
            code=PLATFORM_VIEW_USERS,
            name="View users",
            category="Platform",
        )
    group = UserGroup(name="Security viewers", permissions=[permission])
    db_session.add(group)
    db_session.flush()
    db_session.execute(
        security_user_groups.insert(),
        {"user_id": user.id, "group_id": group.id},
    )
    db_session.commit()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        response = client.get("/api/v1/users")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    items = response.json()["items"]
    emails = [item["email"] for item in items]
    assert user.email in emails


def test_user_organizations_full_lifecycle(api_client, db_session: Session) -> None:
    org = OrganizationRepository(db_session).create(name=f"Org-{uuid4().hex[:8]}")
    target = UserRepository(db_session).create(
        username=f"member-{uuid4().hex[:8]}",
        email=f"member-{uuid4().hex[:8]}@example.com",
        hashed_password="hash",
        is_active=True,
    )
    db_session.commit()

    empty_response = api_client.get(f"/api/v1/users/{target.id}/organizations")
    assert empty_response.status_code == 200
    assert empty_response.json()["organizations"] == []

    user_org_url = f"/api/v1/users/{target.id}/organizations/{org.id}"
    assign_response = api_client.post(user_org_url)
    assert assign_response.status_code == 204

    after_assign = api_client.get(f"/api/v1/users/{target.id}/organizations")
    assert after_assign.status_code == 200
    org_ids = [item["id"] for item in after_assign.json()["organizations"]]
    assert str(org.id) in org_ids

    duplicate_response = api_client.post(user_org_url)
    assert duplicate_response.status_code == 409

    remove_response = api_client.delete(user_org_url)
    assert remove_response.status_code == 204

    after_remove = api_client.get(f"/api/v1/users/{target.id}/organizations")
    assert after_remove.json()["organizations"] == []

    missing_response = api_client.delete(user_org_url)
    assert missing_response.status_code == 404


def test_removing_organization_membership_strips_org_scoped_groups(
    api_client, db_session: Session
) -> None:
    org = OrganizationRepository(db_session).create(name=f"Org-{uuid4().hex[:8]}")
    db_session.flush()  # populate org.id before it is used as a FK below

    target = UserRepository(db_session).create(
        username=f"member-{uuid4().hex[:8]}",
        email=f"member-{uuid4().hex[:8]}@example.com",
        hashed_password="hash",
        is_active=True,
    )
    perm_repo = PermissionRepository(db_session)
    org_group = perm_repo.create_system_group(
        name="Org Viewer",
        description="",
        system_key=f"org-viewer-{uuid4().hex[:8]}",
        organization_id=org.id,
    )
    db_session.flush()

    UsersOrganizationsRepository(db_session).add_member(target.id, org.id)
    db_session.execute(
        security_user_groups.insert(),
        {"user_id": target.id, "group_id": org_group.id},
    )
    db_session.commit()

    assert org_group.id in perm_repo.group_ids_for_user(target.id)

    user_org_url = f"/api/v1/users/{target.id}/organizations/{org.id}"
    remove_response = api_client.delete(user_org_url)
    assert remove_response.status_code == 204

    assert org_group.id not in perm_repo.group_ids_for_user(target.id)


def test_view_only_platform_user_cannot_modify_organization_membership(
    db_session: Session,
) -> None:
    org = OrganizationRepository(db_session).create(name=f"Org-{uuid4().hex[:8]}")
    target = UserRepository(db_session).create(
        username=f"member-{uuid4().hex[:8]}",
        email=f"member-{uuid4().hex[:8]}@example.com",
        hashed_password="hash",
        is_active=True,
    )

    viewer = UserRepository(db_session).create(
        username=f"viewer-{uuid4().hex[:8]}",
        email=f"viewer-{uuid4().hex[:8]}@example.com",
        hashed_password="hash",
        is_active=True,
    )
    perm_repo = PermissionRepository(db_session)
    permission = perm_repo.get_permission_by_code(PLATFORM_VIEW_USERS)
    if not permission:
        permission = perm_repo.create_permission(
            code=PLATFORM_VIEW_USERS,
            name="View users",
            category="Platform",
        )
    group = UserGroup(name=f"Viewer-only-{uuid4().hex[:8]}", permissions=[permission])
    db_session.add(group)
    db_session.flush()
    db_session.execute(
        security_user_groups.insert(),
        {"user_id": viewer.id, "group_id": group.id},
    )
    db_session.commit()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(users_router, prefix="/api/v1")

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: viewer

    with TestClient(app) as client:
        get_response = client.get(f"/api/v1/users/{target.id}/organizations")
        user_org_url = f"/api/v1/users/{target.id}/organizations/{org.id}"
        assign_response = client.post(user_org_url)
        remove_response = client.delete(user_org_url)

    app.dependency_overrides.clear()

    assert get_response.status_code == 200
    assert assign_response.status_code == 403
    assert remove_response.status_code == 403

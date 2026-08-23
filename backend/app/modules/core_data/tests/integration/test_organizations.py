from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.api.organizations import router as organizations_router
from app.modules.core_data.models import User
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.security.dependencies import get_current_user
from app.modules.security.repositories import GroupRepository


def test_organization_repository_filters_and_counts_by_name(
    db_session: Session,
) -> None:
    repo = OrganizationRepository(db_session)
    repo.create(name="TestAcme Water Corp")
    repo.create(name="TestBlue Waters LLC")
    repo.create(name="TestAqua Solutions")
    db_session.commit()

    # Filter by name fragment (case-insensitive ILIKE)
    filtered = repo.list_all(name="water", limit=1000)
    filtered_names = [org.name for org in filtered]
    assert "TestAcme Water Corp" in filtered_names
    assert "TestBlue Waters LLC" in filtered_names
    assert "TestAqua Solutions" not in filtered_names

    # Count with filter
    count = repo.count(name="water")
    assert count >= 2  # At least the two we added

    # Filter for specific org
    filtered2 = repo.list_all(name="Aqua", limit=1000)
    filtered2_names = [org.name for org in filtered2]
    assert "TestAqua Solutions" in filtered2_names


def test_create_organization_seeds_three_starter_groups(
    db_session: Session, admin_user: User
) -> None:
    """Exercises the real DI-wired OrganizationService via the API.

    A prior regression injected the wrong service type (PermissionService
    instead of GroupService) into OrganizationService, so every call to
    _seed_starter_groups() raised AttributeError. No test constructed
    OrganizationService at all, so it went undetected — this test goes
    through the real dependency chain instead of building the service
    by hand.
    """
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(organizations_router, prefix="/api/v1/platform")

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin_user
    client = TestClient(app)

    response = client.post(
        "/api/v1/platform/organizations", json={"name": "Starter Group Test Org"}
    )

    assert response.status_code == 200
    org_id = UUID(response.json()["id"])

    groups = GroupRepository(db_session).list_org_groups(org_id)
    assert len(groups) == 3
    assert {g.is_system for g in groups} == {True}

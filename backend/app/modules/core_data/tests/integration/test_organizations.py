from collections.abc import Generator
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import register_error_handlers
from app.modules.core_data.api.organizations import router as organizations_router
from app.modules.core_data.models import Organization, User
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.security.dependencies import get_current_user


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


def test_admin_can_search_organizations_by_name(db_session: Session) -> None:
    # Setup with unique prefixes to avoid interference from other tests
    org1 = Organization(id=uuid4(), name="AdminTest_Alpha Hydro Systems")
    org2 = Organization(id=uuid4(), name="AdminTest_Beta Water Management")
    org3 = Organization(id=uuid4(), name="AdminTest_Gamma Analytics")
    db_session.add_all([org1, org2, org3])

    admin = User(
        id=uuid4(),
        username="admin_test_search",
        email="admin_test_search@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="User",
        status="admin",
        is_active=True,
        organization_id=None,  # platform admin
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(organizations_router)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: admin

    with TestClient(app) as client:
        response = client.get("/organizations?name=AdminTest_Beta")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "AdminTest_Beta Water Management"


def test_regular_user_sees_only_own_organization_regardless_of_name_filter(
    db_session: Session,
) -> None:
    # Setup
    org1 = Organization(id=uuid4(), name="User Org")
    org2 = Organization(id=uuid4(), name="Other Org")
    db_session.add_all([org1, org2])
    db_session.flush()

    regular_user = User(
        id=uuid4(),
        username="user1",
        email="user1@example.com",
        hashed_password="hash",
        first_name="Regular",
        last_name="User",
        status="regular",
        is_active=True,
        organization_id=org1.id,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(regular_user)
    db_session.commit()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(organizations_router)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: regular_user

    with TestClient(app) as client:
        # Even if filtering by "Other", should only see own org
        response = client.get("/organizations?name=other")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "User Org"


def test_list_organizations_endpoint_allows_any_authenticated_user(
    db_session: Session,
) -> None:
    # Setup minimal org
    org = Organization(id=uuid4(), name="Test Org")
    db_session.add(org)
    db_session.flush()

    user = User(
        id=uuid4(),
        username="user",
        email="user@example.com",
        hashed_password="hash",
        first_name="Test",
        last_name="User",
        status="regular",
        is_active=True,
        organization_id=org.id,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(user)
    db_session.commit()

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(organizations_router)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        response = client.get("/organizations")

    app.dependency_overrides.clear()

    # Should succeed (no permission required)
    assert response.status_code == 200

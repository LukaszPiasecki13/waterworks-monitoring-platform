from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.core_data.models import Organization, User, WaterObject
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.water_objects import ListWaterObjectsRequest
from app.modules.core_data.services.water_objects import WaterObjectService


def test_admin_filtering_by_organization_id_returns_only_that_org_objects(
    db_session: Session,
) -> None:
    # Setup orgs and objects
    org1 = Organization(id=uuid4(), name="Org1_AdminFilter")
    org2 = Organization(id=uuid4(), name="Org2_AdminFilter")
    db_session.add_all([org1, org2])
    db_session.flush()

    obj1 = WaterObject(
        id=uuid4(),
        organization_id=org1.id,
        name="Object in Org1",
        object_type="pump_station",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    obj2 = WaterObject(
        id=uuid4(),
        organization_id=org2.id,
        name="Object in Org2",
        object_type="hydrophore",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([obj1, obj2])

    admin = User(
        id=uuid4(),
        username="admin_water_test",
        email="admin_water_test@example.com",
        hashed_password="hash",
        first_name="Admin",
        last_name="Test",
        status="admin",
        is_active=True,
        organization_id=None,  # platform admin
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()

    # Test filtering by organization_id
    repo = WaterObjectRepository(db_session)
    org_repo = OrganizationRepository(db_session)
    service = WaterObjectService(repo, org_repo, MagicMock())

    query = ListWaterObjectsRequest(organization_id=org1.id)
    objects, count = service.list_all(query, actor=admin)

    assert count == 1
    assert len(objects) == 1
    assert objects[0].organization_id == org1.id
    assert objects[0].name == "Object in Org1"


def test_regular_user_ignores_organization_id_query_param_and_sees_only_own_org(
    db_session: Session,
) -> None:
    # Setup orgs and objects
    user_org = Organization(id=uuid4(), name="UserOrg_FilterTest")
    other_org = Organization(id=uuid4(), name="OtherOrg_FilterTest")
    db_session.add_all([user_org, other_org])
    db_session.flush()

    user_obj = WaterObject(
        id=uuid4(),
        organization_id=user_org.id,
        name="User's Object",
        object_type="intake",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    other_obj = WaterObject(
        id=uuid4(),
        organization_id=other_org.id,
        name="Other Org's Object",
        object_type="network_point",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add_all([user_obj, other_obj])

    regular_user = User(
        id=uuid4(),
        username="user_water_test",
        email="user_water_test@example.com",
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

    # Even if requesting other_org, should only see own org
    repo = WaterObjectRepository(db_session)
    org_repo = OrganizationRepository(db_session)
    service = WaterObjectService(repo, org_repo, MagicMock())

    query = ListWaterObjectsRequest(organization_id=other_org.id)
    objects, count = service.list_all(query, actor=regular_user)

    assert count == 1
    assert len(objects) == 1
    assert objects[0].organization_id == user_org.id
    assert objects[0].name == "User's Object"

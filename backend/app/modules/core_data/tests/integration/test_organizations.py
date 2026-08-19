from sqlalchemy.orm import Session

from app.modules.core_data.repositories.organizations import OrganizationRepository


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

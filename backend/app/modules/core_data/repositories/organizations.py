"""Organization repository for data access."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.organization import Organization


class OrganizationRepository(SQLRepository):
    """Repository for Organization model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, org_id: int) -> Organization | None:
        """Get organization by ID."""
        return self.session.query(Organization).filter(Organization.id == org_id).first()

    def find_by_id(self, org_id: int) -> Organization:
        """Find organization by ID or raise NotFoundError."""
        org = self.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization not found")
        return org

    def get_by_name(self, name: str) -> Organization | None:
        """Get organization by name."""
        return self.session.query(Organization).filter(Organization.name == name).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        """List all organizations."""
        return (
            self.session.query(Organization)
            .order_by(Organization.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        """Count all organizations."""
        return self.session.query(func.count(Organization.id)).scalar() or 0

    def create(self, name: str) -> Organization:
        """Create new organization."""
        org = Organization(name=name)
        self.session.add(org)
        return org

    def update(self, org: Organization, *, name: str | None = None) -> Organization:
        """Update organization fields."""
        if name is not None:
            org.name = name
        return org

    def delete(self, org: Organization) -> None:
        """Delete organization."""
        self.session.delete(org)

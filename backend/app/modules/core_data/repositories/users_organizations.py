"""User-organization membership repository for data access."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.models.organization import Organization
from app.modules.core_data.models.user import User
from app.modules.core_data.models.users_organizations import UsersOrganizations


class UsersOrganizationsRepository(SQLRepository):
    """Repository for UsersOrganizations model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def add_member(self, user_id: UUID, organization_id: UUID) -> UsersOrganizations:
        """Add user to organization."""
        membership = UsersOrganizations(
            user_id=user_id, organization_id=organization_id
        )
        self.session.add(membership)
        return membership

    def remove_member(self, user_id: UUID, organization_id: UUID) -> None:
        """Remove user from organization."""
        self.session.query(UsersOrganizations).filter(
            UsersOrganizations.user_id == user_id,
            UsersOrganizations.organization_id == organization_id,
        ).delete()

    def is_member(self, user_id: UUID, organization_id: UUID) -> bool:
        """Check if user is member of organization."""
        return (
            self.session.query(UsersOrganizations)
            .filter(
                UsersOrganizations.user_id == user_id,
                UsersOrganizations.organization_id == organization_id,
            )
            .first()
            is not None
        )

    def list_member_organizations(self, user_id: UUID) -> list[UUID]:
        """List all organizations user is member of."""
        members = (
            self.session.query(UsersOrganizations.organization_id)
            .filter(UsersOrganizations.user_id == user_id)
            .all()
        )
        return [m[0] for m in members]

    def count_organization_members(self, organization_id: UUID) -> int:
        """Count members in organization."""
        return (
            self.session.query(func.count(UsersOrganizations.user_id))
            .filter(UsersOrganizations.organization_id == organization_id)
            .scalar()
            or 0
        )

    def list_members(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """List users who are members of the given organization."""
        stmt = (
            select(User)
            .join(UsersOrganizations, UsersOrganizations.user_id == User.id)
            .where(UsersOrganizations.organization_id == organization_id)
            .order_by(User.last_name, User.first_name, User.email)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_organization(self, organization_id: UUID) -> Organization | None:
        """Get organization by ID."""
        return (
            self.session.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )

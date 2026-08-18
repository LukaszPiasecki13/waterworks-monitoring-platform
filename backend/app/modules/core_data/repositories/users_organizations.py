"""User-organization membership repository for data access."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
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

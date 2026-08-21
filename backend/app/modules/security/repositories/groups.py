"""Data access for user groups and their members."""

from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.security.models import UserGroup, security_user_groups


class GroupRepository(SQLRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_group(self, group_id: UUID) -> UserGroup | None:
        return self.session.query(UserGroup).filter_by(id=group_id).first()

    def get_group_for_update(self, group_id: UUID) -> UserGroup | None:
        return (
            self.session.query(UserGroup)
            .filter_by(id=group_id)
            .with_for_update()
            .first()
        )

    def get_group_by_system_key(
        self, system_key: str, organization_id: UUID | None = None
    ) -> UserGroup | None:
        query = self.session.query(UserGroup).filter_by(system_key=system_key)
        if organization_id is None:
            query = query.filter(UserGroup.organization_id.is_(None))
        else:
            query = query.filter(UserGroup.organization_id == organization_id)
        return query.first()

    def get_group_by_system_key_for_update(
        self, system_key: str, organization_id: UUID | None = None
    ) -> UserGroup | None:
        query = self.session.query(UserGroup).filter_by(system_key=system_key)
        if organization_id is None:
            query = query.filter(UserGroup.organization_id.is_(None))
        else:
            query = query.filter(UserGroup.organization_id == organization_id)
        return query.with_for_update().first()

    def create_group(
        self, *, name: str, description: str, organization_id: UUID | None = None
    ) -> UserGroup:
        group = UserGroup(
            name=name, description=description, organization_id=organization_id
        )
        self.session.add(group)
        return group

    def create_system_group(
        self,
        *,
        name: str,
        description: str,
        system_key: str,
        organization_id: UUID | None = None,
        permissions: list | None = None,
    ) -> UserGroup:
        group = UserGroup(
            name=name,
            description=description,
            is_system=True,
            system_key=system_key,
            organization_id=organization_id,
            permissions=permissions or [],
        )
        self.session.add(group)
        return group

    def delete_group(self, group: UserGroup) -> None:
        self.session.delete(group)

    def list_groups(self) -> list[UserGroup]:
        return (
            self.session.query(UserGroup)
            .order_by(UserGroup.is_system.desc(), UserGroup.name)
            .all()
        )

    def list_platform_groups(self) -> list[UserGroup]:
        """List platform-level groups only (organization_id IS NULL)."""
        return (
            self.session.query(UserGroup)
            .filter(UserGroup.organization_id.is_(None))
            .order_by(UserGroup.is_system.desc(), UserGroup.name)
            .all()
        )

    def list_org_groups(self, organization_id: UUID) -> list[UserGroup]:
        """List groups for a specific organization."""
        return (
            self.session.query(UserGroup)
            .filter(UserGroup.organization_id == organization_id)
            .order_by(UserGroup.is_system.desc(), UserGroup.name)
            .all()
        )

    def list_groups_for_organization(
        self, organization_id: UUID | None
    ) -> list[UserGroup]:
        """List groups scoped to one plane: a single organization, or the
        platform plane when organization_id is None. Used for name-uniqueness
        checks so they never leak across organizations (or into/out of the
        platform plane)."""
        query = self.session.query(UserGroup)
        if organization_id is None:
            query = query.filter(UserGroup.organization_id.is_(None))
        else:
            query = query.filter(UserGroup.organization_id == organization_id)
        return query.all()

    def group_ids_for_organization(self, organization_id: UUID) -> list[UUID]:
        """IDs grup należących do danej organizacji (nie platformowych)."""
        statement = select(UserGroup.id).where(
            UserGroup.organization_id == organization_id
        )
        return list(self.session.execute(statement).scalars().all())

    def group_ids_for_user(self, user_id: UUID) -> list[UUID]:
        statement = select(security_user_groups.c.group_id).where(
            security_user_groups.c.user_id == user_id
        )
        return list(self.session.execute(statement).scalars().all())

    def user_ids_for_group(self, group_id: UUID) -> list[UUID]:
        statement = select(security_user_groups.c.user_id).where(
            security_user_groups.c.group_id == group_id
        )
        return list(self.session.execute(statement).scalars().all())

    def replace_user_groups(self, user_id: UUID, group_ids: set[UUID]) -> None:
        self.session.execute(
            delete(security_user_groups).where(
                security_user_groups.c.user_id == user_id
            )
        )
        if group_ids:
            self.session.execute(
                insert(security_user_groups),
                [{"user_id": user_id, "group_id": group_id} for group_id in group_ids],
            )

    def replace_group_users(self, group_id: UUID, user_ids: set[UUID]) -> None:
        self.session.execute(
            delete(security_user_groups).where(
                security_user_groups.c.group_id == group_id
            )
        )
        if user_ids:
            self.session.execute(
                insert(security_user_groups),
                [{"user_id": user_id, "group_id": group_id} for user_id in user_ids],
            )

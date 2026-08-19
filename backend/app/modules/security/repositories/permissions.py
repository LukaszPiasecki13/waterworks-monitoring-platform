"""Data access for user groups and permissions."""

from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.security.models import (
    Permission,
    UserGroup,
    security_user_groups,
)


class PermissionRepository(SQLRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_permission_by_code(self, code: str) -> Permission | None:
        return self.session.query(Permission).filter_by(code=code).first()

    def create_permission(self, *, code: str, name: str, category: str) -> Permission:
        permission = Permission(code=code, name=name, category=category)
        self.session.add(permission)
        return permission

    def create_system_group(
        self,
        *,
        name: str,
        description: str,
        system_key: str,
        permissions: list[Permission] | None = None,
    ) -> UserGroup:
        group = UserGroup(
            name=name,
            description=description,
            is_system=True,
            system_key=system_key,
            permissions=permissions or [],
        )
        self.session.add(group)
        return group

    def list_permissions(self) -> list[Permission]:
        return (
            self.session.query(Permission)
            .order_by(Permission.category, Permission.name)
            .all()
        )

    def get_permissions_by_codes(self, codes: set[str]) -> list[Permission]:
        if not codes:
            return []
        return self.session.query(Permission).filter(Permission.code.in_(codes)).all()

    def list_groups(self) -> list[UserGroup]:
        return (
            self.session.query(UserGroup)
            .order_by(UserGroup.is_system.desc(), UserGroup.name)
            .all()
        )

    def get_group(self, group_id: UUID) -> UserGroup | None:
        return self.session.query(UserGroup).filter_by(id=group_id).first()

    def get_group_for_update(self, group_id: UUID) -> UserGroup | None:
        return (
            self.session.query(UserGroup)
            .filter_by(id=group_id)
            .with_for_update()
            .first()
        )

    def get_group_by_system_key(self, system_key: str) -> UserGroup | None:
        return self.session.query(UserGroup).filter_by(system_key=system_key).first()

    def get_group_by_system_key_for_update(self, system_key: str) -> UserGroup | None:
        return (
            self.session.query(UserGroup)
            .filter_by(system_key=system_key)
            .with_for_update()
            .first()
        )

    def create_group(self, *, name: str, description: str) -> UserGroup:
        group = UserGroup(name=name, description=description)
        self.session.add(group)
        return group

    def delete_group(self, group: UserGroup) -> None:
        self.session.delete(group)

    def permission_codes_for_user(self, user_id: UUID) -> set[str]:
        statement = (
            select(Permission.code)
            .join(UserGroup.permissions)
            .join(security_user_groups, security_user_groups.c.group_id == UserGroup.id)
            .where(security_user_groups.c.user_id == user_id)
        )
        return set(self.session.execute(statement).scalars().all())

    def permission_codes_for_user_in_org(
        self, user_id: UUID, organization_id: UUID
    ) -> set[str]:
        """Get permission codes for user in specific organization.

        Union of platform-level groups (organization_id IS NULL)
        and organization-specific groups (organization_id == provided org).
        """
        statement = (
            select(Permission.code)
            .join(UserGroup.permissions)
            .join(security_user_groups, security_user_groups.c.group_id == UserGroup.id)
            .where(
                security_user_groups.c.user_id == user_id,
                (UserGroup.organization_id.is_(None))
                | (UserGroup.organization_id == organization_id),
            )
        )
        return set(self.session.execute(statement).scalars().all())

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

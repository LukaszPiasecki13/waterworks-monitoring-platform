"""Data access for permissions (read-only)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.security.models import Permission, UserGroup, security_user_groups


class PermissionRepository(SQLRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_permission_by_code(self, code: str) -> Permission | None:
        return self.session.query(Permission).filter_by(code=code).first()

    def create_permission(self, *, code: str, name: str, category: str) -> Permission:
        permission = Permission(code=code, name=name, category=category)
        self.session.add(permission)
        return permission

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

    def permission_codes_for_user_at_platform_level(self, user_id: UUID) -> set[str]:
        """Get platform-level permission codes for user.

        Only returns permissions from groups where organization_id IS NULL.
        """
        statement = (
            select(Permission.code)
            .join(UserGroup.permissions)
            .join(security_user_groups, security_user_groups.c.group_id == UserGroup.id)
            .where(
                security_user_groups.c.user_id == user_id,
                UserGroup.organization_id.is_(None),
            )
        )
        return set(self.session.execute(statement).scalars().all())

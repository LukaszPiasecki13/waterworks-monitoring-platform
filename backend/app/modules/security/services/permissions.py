"""Permission resolution and user permission queries."""

from uuid import UUID

from app.core.errors import ValidationException
from app.modules.core_data.models import User
from app.modules.core_data.repositories.users import UserRepository
from app.modules.security.models import Permission
from app.modules.security.repositories.groups import GroupRepository
from app.modules.security.repositories.permissions import PermissionRepository


class PermissionService:
    def __init__(
        self,
        repo: PermissionRepository,
        users: UserRepository,
        group_repo: GroupRepository | None = None,
    ):
        self.repo = repo
        self.users = users
        self.group_repo = group_repo

    def permissions_for_user(self, user: User) -> set[str]:
        return self.repo.permission_codes_for_user(user.id)

    def permissions_for_user_in_org(
        self, user: User, organization_id: UUID
    ) -> set[str]:
        return self.repo.permission_codes_for_user_in_org(user.id, organization_id)

    def permissions_for_user_at_platform_level(self, user: User) -> set[str]:
        return self.repo.permission_codes_for_user_at_platform_level(user.id)

    def has_permission(self, user: User, permission_code: str) -> bool:
        return permission_code in self.permissions_for_user(user)

    def list_permissions(self):
        return self.repo.list_permissions()

    def group_ids_for_user(self, user_id: UUID) -> list[UUID]:
        """Get group IDs for a user. Used in /me/permissions endpoint."""
        if not self.group_repo:
            return []
        return sorted(self.group_repo.group_ids_for_user(user_id))

    def resolve_permissions(
        self, codes: list[str], *, organization_id: UUID | None
    ) -> list[Permission]:
        """Resolve permission codes and validate plane membership.

        Platform groups (organization_id IS NULL) may only contain PLATFORM_* codes.
        Organization groups must only contain CAN_* codes.
        """
        unique_codes = set(codes)
        permissions = self.repo.get_permissions_by_codes(unique_codes)
        found_codes = {permission.code for permission in permissions}
        unknown = unique_codes - found_codes
        if unknown:
            raise ValidationException(
                f"Nieznane uprawnienia: {', '.join(sorted(unknown))}"
            )

        if organization_id is None:
            invalid = {c for c in found_codes if not c.startswith("PLATFORM_")}
            if invalid:
                raise ValidationException(
                    f"Grupy platformowe mogą zawierać wyłącznie uprawnienia "
                    f"PLATFORM_*. Niedozwolone kody: {', '.join(sorted(invalid))}"
                )
        else:
            invalid = {c for c in found_codes if c.startswith("PLATFORM_")}
            if invalid:
                raise ValidationException(
                    f"Grupy organizacyjne mogą zawierać wyłącznie uprawnienia CAN_*. "
                    f"Niedozwolone kody: {', '.join(sorted(invalid))}"
                )

        return permissions

"""User group management and membership rules."""

from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)
from app.modules.core_data.models import User
from app.modules.core_data.repositories.users import UserRepository
from app.modules.security.audit_state import security_group_audit_state
from app.modules.security.models import UserGroup
from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    STAFF_GROUP_KEY,
)
from app.modules.security.repositories.groups import GroupRepository
from app.modules.security.schemas.groups import (
    UserGroupCreateRequest,
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
)
from app.modules.security.services.permissions import PermissionService


class GroupService:
    def __init__(
        self,
        repo: GroupRepository,
        users: UserRepository,
        permissions: PermissionService,
        audit: AuditPort,
    ):
        self.repo = repo
        self.users = users
        self.permissions = permissions
        self.audit = audit

    def _group_state(self, group: UserGroup) -> dict:
        return security_group_audit_state(group, self.repo.user_ids_for_group(group.id))

    def _record_group(
        self,
        action: str,
        group: UserGroup,
        actor: User,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.SECURITY_USER_GROUP.value,
                entity_id=str(group.id),
                action=action,
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def _record_user_groups(
        self,
        user: User,
        actor: User,
        old_group_ids: list[UUID],
        new_group_ids: list[UUID],
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_USER.value,
                entity_id=str(user.id),
                action="SECURITY_GROUPS_UPDATE",
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(
                    {"security_group_ids": sorted(old_group_ids)},
                    {"security_group_ids": sorted(new_group_ids)},
                ),
            )
        )

    def _capture_user_groups(self, user_ids: set[UUID]) -> dict[UUID, list[UUID]]:
        return {
            user_id: sorted(self.repo.group_ids_for_user(user_id))
            for user_id in user_ids
        }

    def _record_membership_changes(
        self,
        before: dict[UUID, list[UUID]],
        actor: User,
    ) -> None:
        for user_id, old_group_ids in before.items():
            new_group_ids = sorted(self.repo.group_ids_for_user(user_id))
            if old_group_ids == new_group_ids:
                continue
            user = self.users.get_by_id(user_id)
            if user:
                self._record_user_groups(user, actor, old_group_ids, new_group_ids)

    def list_groups(self) -> list[dict]:
        return [self._serialize_group(group) for group in self.repo.list_groups()]

    def list_platform_groups(self) -> list[dict]:
        """List platform-level groups (organization_id IS NULL)."""
        return [
            self._serialize_group(group) for group in self.repo.list_platform_groups()
        ]

    def list_org_groups(self, organization_id: UUID) -> list[dict]:
        """List groups for a specific organization."""
        return [
            self._serialize_group(group)
            for group in self.repo.list_org_groups(organization_id)
        ]

    def get_group(self, group_id: UUID) -> UserGroup:
        group = self.repo.get_group(group_id)
        if not group:
            raise NotFoundError("Grupa użytkowników nie istnieje")
        return group

    def get_org_group(self, group_id: UUID, org_id: UUID) -> UserGroup:
        """Get group, ensuring it belongs to the specified organization.

        Raises NotFoundError (404) if group doesn't exist or belongs to different org.
        Used to prevent IDOR attacks on cross-org access — 404 instead of 403 ensures
        an attacker can't enumerate whether an org exists.
        """
        group = self.get_group(group_id)
        if group.organization_id != org_id:
            raise NotFoundError("Grupa użytkowników nie istnieje")
        return group

    def _validate_group_name(
        self,
        name: str,
        *,
        group_id: UUID | None,
        organization_id: UUID | None,
    ) -> None:
        """Uniqueness check scoped to one plane (org or platform) — never
        compares across organizations, so two orgs may both have a group
        named "Operator" without colliding (matches DB constraint
        UNIQUE(organization_id, name))."""
        duplicate = any(
            candidate.name.casefold() == name.casefold()
            and (group_id is None or candidate.id != group_id)
            for candidate in self.repo.list_groups_for_organization(organization_id)
        )
        if duplicate:
            raise ConflictError("Grupa o tej nazwie już istnieje")

    def create_group(
        self,
        request: UserGroupCreateRequest,
        *,
        actor: User,
        organization_id: UUID | None = None,
    ) -> dict:
        with self.repo.transaction():
            self._validate_group_name(
                request.name, group_id=None, organization_id=organization_id
            )
            group = self.repo.create_group(
                name=request.name,
                description=request.description,
                organization_id=organization_id,
            )
            group.permissions = self.permissions.resolve_permissions(
                request.permission_codes, organization_id=group.organization_id
            )
            self.repo.flush()
            self.repo.refresh(group)
            self._record_group("CREATE", group, actor, {}, self._group_state(group))
            return self._serialize_group(group)

    def update_group(
        self,
        group_id: UUID,
        request: UserGroupUpdateRequest,
        actor: User,
    ) -> dict:
        with self.repo.transaction() as tx:
            group = self.get_group(group_id)
            old_state = self._group_state(group)
            self._ensure_custom_group(group)
            if request.name is not None:
                self._validate_group_name(
                    request.name,
                    group_id=group.id,
                    organization_id=group.organization_id,
                )
                group.name = request.name
            if request.description is not None:
                group.description = request.description
            self.repo.flush()
            self.repo.refresh(group)
            new_state = self._group_state(group)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return self._serialize_group(group)
            self._record_group("UPDATE", group, actor, old_state, new_state)
            return self._serialize_group(group)

    def replace_group_permissions(
        self, group_id: UUID, codes: list[str], actor: User
    ) -> dict:
        with self.repo.transaction() as tx:
            group = self.get_group(group_id)
            old_state = self._group_state(group)
            self._ensure_permissions_editable(group)
            group.permissions = self.permissions.resolve_permissions(
                codes, organization_id=group.organization_id
            )
            self.repo.flush()
            self.repo.refresh(group)
            new_state = self._group_state(group)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return self._serialize_group(group)
            self._record_group("PERMISSIONS_UPDATE", group, actor, old_state, new_state)
            return self._serialize_group(group)

    def save_group(
        self,
        group_id: UUID,
        request: UserGroupSaveRequest,
        *,
        actor: User,
    ) -> dict:
        """Save metadata, permissions and members atomically."""

        with self.repo.transaction() as tx:
            group = self.repo.get_group_for_update(group_id)
            if not group:
                raise NotFoundError("Grupa użytkowników nie istnieje")
            old_state = self._group_state(group)
            member_ids = set(request.user_ids)
            changed_user_ids: set[UUID] = set(old_state["user_ids"]) ^ member_ids
            user_groups_before = self._capture_user_groups(changed_user_ids)
            self._validate_users(member_ids)
            self._protect_last_admin(group, member_ids)

            if group.is_system:
                if (
                    request.name != group.name
                    or request.description != group.description
                ):
                    raise BadRequestError(
                        "Nazwy i opisu grupy systemowej nie można zmieniać"
                    )
                current_codes = {permission.code for permission in group.permissions}
                if set(request.permission_codes) != current_codes:
                    self._ensure_permissions_editable(group)
                    group.permissions = self.permissions.resolve_permissions(
                        request.permission_codes, organization_id=group.organization_id
                    )
            else:
                self._validate_group_name(
                    request.name,
                    group_id=group.id,
                    organization_id=group.organization_id,
                )
                group.name = request.name
                group.description = request.description
                group.permissions = self.permissions.resolve_permissions(
                    request.permission_codes, organization_id=group.organization_id
                )

            self.repo.replace_group_users(group.id, member_ids)
            self.repo.flush()
            self.repo.refresh(group)
            new_state = self._group_state(group)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return self._serialize_group(group)
            self._record_group("UPDATE", group, actor, old_state, new_state)
            self._record_membership_changes(user_groups_before, actor)
            return self._serialize_group(group)

    def replace_group_users(
        self, group_id: UUID, user_ids: list[UUID], actor: User
    ) -> dict:
        with self.repo.transaction() as tx:
            group = self.repo.get_group_for_update(group_id)
            if not group:
                raise NotFoundError("Grupa użytkowników nie istnieje")
            old_state = self._group_state(group)
            ids = set(user_ids)
            changed_user_ids = set(old_state["user_ids"]) ^ ids
            user_groups_before = self._capture_user_groups(changed_user_ids)
            self._validate_users(ids)
            self._protect_last_admin(group, ids)
            self.repo.replace_group_users(group_id, ids)
            self.repo.flush()
            new_state = self._group_state(group)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return self._serialize_group(group)
            self._record_group("MEMBERS_UPDATE", group, actor, old_state, new_state)
            self._record_membership_changes(user_groups_before, actor)
            return self._serialize_group(group)

    def replace_user_groups(
        self, user_id: UUID, group_ids: list[UUID], actor: User
    ) -> list[UUID]:
        with self.repo.transaction() as tx:
            user = self.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("Użytkownik nie istnieje")
            ids = set(group_ids)
            old_ids = sorted(self.repo.group_ids_for_user(user_id))
            changed_group_ids = set(old_ids) ^ ids
            group_states_before = {
                group_id: self._group_state(self.get_group(group_id))
                for group_id in changed_group_ids
            }
            for group_id in ids:
                self.get_group(group_id)
            admin_group = self.repo.get_group_by_system_key_for_update(
                ADMIN_GROUP_KEY, organization_id=None
            )
            if admin_group:
                existing_admins = set(self.repo.user_ids_for_group(admin_group.id))
                if (
                    user_id in existing_admins
                    and admin_group.id not in ids
                    and len(existing_admins) == 1
                ):
                    raise BadRequestError(
                        "Nie można usunąć ostatniego użytkownika z grupy Admin"
                    )
            self.repo.replace_user_groups(user_id, ids)
            self.repo.flush()
            new_ids = sorted(ids)
            if old_ids == new_ids:
                tx.skip_audit()
                return old_ids
            self._record_user_groups(user, actor, old_ids, new_ids)
            for group_id, old_state in group_states_before.items():
                group = self.get_group(group_id)
                self._record_group(
                    "MEMBERS_UPDATE",
                    group,
                    actor,
                    old_state,
                    self._group_state(group),
                )
            return sorted(ids)

    def remove_system_group(
        self, user: User, system_key: str, actor: User | None = None
    ) -> None:
        """Remove one lifecycle group while preserving all other memberships."""
        group = self.repo.get_group_by_system_key(system_key)
        if group is None:
            return
        current = set(self.repo.group_ids_for_user(user.id))
        if group.id in current:
            old_state = self._group_state(group) if actor else None
            current.remove(group.id)
            self.repo.replace_user_groups(user.id, current)
            if actor and old_state:
                self.repo.flush()
                self._record_group(
                    "MEMBERS_UPDATE",
                    group,
                    actor,
                    old_state,
                    self._group_state(group),
                )

    def delete_group(self, group_id: UUID, actor: User) -> None:
        with self.repo.transaction():
            group = self.get_group(group_id)
            old_state = self._group_state(group)
            affected_user_ids = set(old_state["user_ids"])
            user_groups_before = self._capture_user_groups(affected_user_ids)
            self._ensure_custom_group(group)
            self.repo.delete_group(group)
            self.repo.flush()
            self._record_group("DELETE", group, actor, old_state, {})
            self._record_membership_changes(user_groups_before, actor)

    def group_ids_for_user(self, user_id: UUID) -> list[UUID]:
        if not self.users.get_by_id(user_id):
            raise NotFoundError("Użytkownik nie istnieje")
        return sorted(self.repo.group_ids_for_user(user_id))

    def seed_organization_groups(
        self,
        organization_id: UUID,
        org_plane_codes: set[str],
        view_codes: set[str],
        admin_key: str,
        operator_key: str,
        viewer_key: str,
        actor: User,
    ) -> None:
        """Create 3 starter groups for organization during creation."""
        all_perms = self.permissions.list_permissions()
        org_perms = [p for p in all_perms if p.code in org_plane_codes]
        view_perms = [p for p in org_perms if p.code in view_codes]
        manage_assets_code = next(
            (c for c in org_plane_codes if "MANAGE_ASSETS" in c), None
        )
        operator_perms = [
            p for p in org_perms if p.code in view_codes or p.code == manage_assets_code
        ]

        groups = [
            self.repo.create_system_group(
                name="Administrator organizacji",
                description="Pełny dostęp do zarządzania gminą",
                system_key=admin_key,
                organization_id=organization_id,
                permissions=org_perms,
            ),
            self.repo.create_system_group(
                name="Operator",
                description="Zarządzanie obiektami i urządzeniami, podgląd reszty",
                system_key=operator_key,
                organization_id=organization_id,
                permissions=operator_perms,
            ),
            self.repo.create_system_group(
                name="Podgląd",
                description="Dostęp wyłącznie do podglądu",
                system_key=viewer_key,
                organization_id=organization_id,
                permissions=view_perms,
            ),
        ]
        self.repo.flush()
        for group in groups:
            self.repo.refresh(group)
            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.SECURITY_USER_GROUP.value,
                    entity_id=str(group.id),
                    action="CREATE",
                    actor_id=str(actor.id),
                    actor_display_name=actor.email,
                    changes={"name": {"old": None, "new": group.name}},
                    context_type="core_data_organization",
                    context_id=str(organization_id),
                )
            )

    def _validate_users(self, user_ids: set[UUID]) -> None:
        missing = [user_id for user_id in user_ids if not self.users.get_by_id(user_id)]
        if missing:
            raise NotFoundError(f"Nie istnieją użytkownicy: {missing}")

    def _protect_last_admin(self, group: UserGroup, new_user_ids: set[UUID]) -> None:
        if group.system_key != ADMIN_GROUP_KEY:
            return
        if not new_user_ids:
            raise BadRequestError(
                "Grupa Admin musi mieć co najmniej jednego użytkownika"
            )

    @staticmethod
    def _ensure_custom_group(group: UserGroup) -> None:
        if group.is_system:
            raise BadRequestError("Grupy systemowej nie można modyfikować")

    @staticmethod
    def _ensure_permissions_editable(group: UserGroup) -> None:
        """STAFF permissions are admin-tunable; other system groups stay locked
        — Admin especially, so administrators cannot cut off their own access."""
        if group.is_system and group.system_key != STAFF_GROUP_KEY:
            raise BadRequestError(
                "Uprawnień tej grupy systemowej nie można modyfikować"
            )

    def _serialize_group(self, group: UserGroup) -> dict:
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "is_system": group.is_system,
            "system_key": group.system_key,
            "organization_id": (
                str(group.organization_id) if group.organization_id else None
            ),
            "permissions": sorted(
                group.permissions, key=lambda item: (item.category, item.name)
            ),
            "user_ids": sorted(self.repo.user_ids_for_group(group.id)),
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        }

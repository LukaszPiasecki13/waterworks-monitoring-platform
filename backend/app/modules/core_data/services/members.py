"""Organization membership management service."""

from typing import TYPE_CHECKING
from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType
from app.core.errors import ConflictError, NotFoundError
from app.modules.core_data.models.organization import Organization
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.users_organizations import (
    UsersOrganizationsRepository,
)
from app.modules.core_data.services.users import UserService
from app.modules.security.services.groups import GroupService

if TYPE_CHECKING:
    from app.modules.security.access import OrganizationAccess


class MembersService:
    """Manage which users belong to an organization."""

    def __init__(
        self,
        repo: UsersOrganizationsRepository,
        user_service: UserService,
        groups: GroupService,
        audit: AuditPort,
    ):
        self.repo = repo
        self.user_service = user_service
        self.groups = groups
        self.audit = audit

    def list_members(self, org_access: OrganizationAccess, skip: int, limit: int):
        members = self.repo.list_members(org_access.organization_id, skip, limit)
        total = self.repo.count_organization_members(org_access.organization_id)
        return members, total

    def add_member(self, user_id: UUID, org_access: OrganizationAccess) -> User:
        user = self.user_service.get_user_by_id(user_id, actor=org_access.actor)
        if self.repo.is_member(user_id, org_access.organization_id):
            raise ConflictError("User is already a member of this organization")

        with self.repo.transaction():
            self.repo.add_member(user_id, org_access.organization_id)
            self.repo.flush()

            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.CORE_DATA_USER.value,
                    entity_id=str(user_id),
                    action="ORGANIZATION_MEMBER_ADD",
                    actor_id=str(org_access.actor.id),
                    actor_display_name=org_access.actor.email,
                    changes={
                        "organization_id": {
                            "old": None,
                            "new": str(org_access.organization_id),
                        }
                    },
                    context_type="core_data_organization",
                    context_id=str(org_access.organization_id),
                )
            )

        self.groups.sync_org_membership_group(
            user_id,
            org_access.organization_id,
            joined=True,
            actor=org_access.actor,
        )
        return user

    def remove_member(self, user_id: UUID, org_access: OrganizationAccess) -> None:
        if not self.repo.is_member(user_id, org_access.organization_id):
            raise NotFoundError("User is not a member of this organization")

        with self.repo.transaction():
            self.repo.remove_member(user_id, org_access.organization_id)
            self.repo.flush()
            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.CORE_DATA_USER.value,
                    entity_id=str(user_id),
                    action="ORGANIZATION_MEMBER_REMOVE",
                    actor_id=str(org_access.actor.id),
                    actor_display_name=org_access.actor.email,
                    changes={
                        "organization_id": {
                            "old": str(org_access.organization_id),
                            "new": None,
                        }
                    },
                    context_type="core_data_organization",
                    context_id=str(org_access.organization_id),
                )
            )

        self.groups.sync_org_membership_group(
            user_id,
            org_access.organization_id,
            joined=False,
            actor=org_access.actor,
        )

    def get_organizations_for_user(self, user_id: UUID) -> list[Organization]:
        """Get all organizations user is a member of, with full org details."""
        org_ids = self.repo.list_member_organizations(user_id)
        organizations = []
        for org_id in org_ids:
            org = self.repo.get_organization(org_id)
            if org:
                organizations.append(org)
        return organizations

    def assign_user_to_organization(
        self, user_id: UUID, organization_id: UUID, actor: User
    ) -> None:
        """Assign a user to an organization (platform-admin perspective)."""
        self.user_service.get_user_by_id(user_id, actor=actor)  # 404 if not found
        if self.repo.is_member(user_id, organization_id):
            raise ConflictError("User is already a member of this organization")

        with self.repo.transaction():
            self.repo.add_member(user_id, organization_id)
            self.repo.flush()
            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.CORE_DATA_USER.value,
                    entity_id=str(user_id),
                    action="ORGANIZATION_MEMBER_ADD",
                    actor_id=str(actor.id),
                    actor_display_name=actor.email,
                    changes={
                        "organization_id": {
                            "old": None,
                            "new": str(organization_id),
                        }
                    },
                    context_type="core_data_organization",
                    context_id=str(organization_id),
                )
            )

        self.groups.sync_org_membership_group(
            user_id, organization_id, joined=True, actor=actor
        )

    def remove_user_from_organization(
        self, user_id: UUID, organization_id: UUID, actor: User
    ) -> None:
        """Remove a user from an organization (platform-admin perspective)."""
        if not self.repo.is_member(user_id, organization_id):
            raise NotFoundError("User is not a member of this organization")

        with self.repo.transaction():
            self.repo.remove_member(user_id, organization_id)
            self.repo.flush()
            self.audit.record(
                AuditEntry(
                    entity_type=EntityType.CORE_DATA_USER.value,
                    entity_id=str(user_id),
                    action="ORGANIZATION_MEMBER_REMOVE",
                    actor_id=str(actor.id),
                    actor_display_name=actor.email,
                    changes={
                        "organization_id": {
                            "old": str(organization_id),
                            "new": None,
                        },
                    },
                    context_type="core_data_organization",
                    context_id=str(organization_id),
                )
            )

        self.groups.sync_org_membership_group(
            user_id, organization_id, joined=False, actor=actor
        )

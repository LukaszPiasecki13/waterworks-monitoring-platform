"""Organization management service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.core_data.models.organization import Organization
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.schemas.organizations import (
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
)
from app.modules.security.permission_catalog import (
    ORG_ADMIN_GROUP_KEY,
    ORG_OPERATOR_GROUP_KEY,
    ORG_PLANE_PERMISSION_CODES,
    ORG_VIEWER_GROUP_KEY,
    VIEW_PERMISSIONS,
)
from app.modules.security.services.groups import GroupService


class OrganizationService:
    """Service for organization management operations."""

    def __init__(
        self,
        repo: OrganizationRepository,
        group_service: GroupService,
        audit: AuditPort,
    ):
        self.repo = repo
        self.group_service = group_service
        self.audit = audit

    def _state(self, org) -> dict:
        return {"name": org.name}

    def _record_audit(
        self,
        action: str,
        org,
        actor: User,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_ORGANIZATION.value,
                entity_id=str(org.id),
                action=action,
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, org_id: UUID, actor: User):
        """Get organization by ID."""
        return self.repo.find_by_id(org_id)

    def list_all(self, query, *, actor: User):
        """List organizations (permission-gated by CAN_VIEW_ORGANIZATIONS)."""
        orgs = self.repo.list_all(skip=query.skip, limit=query.limit, name=query.name)
        count = self.repo.count(name=query.name)
        return orgs, count

    def create(self, request: OrganizationCreateRequest, *, actor: User):
        """Create organization with 3 starter security groups."""
        with self.repo.transaction():
            if self.repo.get_by_name(request.name):
                raise ConflictError(f"Organization '{request.name}' already exists")
            org = self.repo.create(name=request.name)
            self.repo.flush()
            self.repo.refresh(org)
            self._seed_starter_groups(org, actor)
            self._record_audit("CREATE", org, actor, {}, self._state(org))
            return org

    def _seed_starter_groups(self, org: Organization, actor: User) -> None:
        """Create 3 starter groups for organization."""
        self.group_service.seed_organization_groups(
            organization_id=org.id,
            org_plane_codes=ORG_PLANE_PERMISSION_CODES,
            view_codes=VIEW_PERMISSIONS,
            admin_key=ORG_ADMIN_GROUP_KEY,
            operator_key=ORG_OPERATOR_GROUP_KEY,
            viewer_key=ORG_VIEWER_GROUP_KEY,
            actor=actor,
        )

    def update(self, org_id: UUID, request: OrganizationUpdateRequest, actor: User):
        """Update organization."""
        with self.repo.transaction() as tx:
            org = self.get_by_id(org_id, actor)
            old_state = self._state(org)
            if request.name is not None:
                existing = self.repo.get_by_name(request.name)
                if existing and existing.id != org.id:
                    raise ConflictError("Organization name already exists")
            self.repo.update(org, name=request.name)
            self.repo.flush()
            self.repo.refresh(org)
            new_state = self._state(org)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return org
            self._record_audit("UPDATE", org, actor, old_state, new_state)
            return org

    def delete(self, org_id: UUID, actor: User) -> None:
        """Delete organization."""
        try:
            with self.repo.transaction():
                org = self.get_by_id(org_id, actor)
                old_state = self._state(org)
                self.repo.delete(org)
                self._record_audit("DELETE", org, actor, old_state, {})
        except IntegrityError as err:
            raise ConflictError(
                "Cannot delete organization with related objects"
            ) from err

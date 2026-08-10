"""Organization management service."""

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError, NotFoundError
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.schemas.organizations import (
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
)


class OrganizationService:
    """Service for organization management operations."""

    def __init__(
        self,
        repo: OrganizationRepository,
        audit: AuditPort,
    ):
        self.repo = repo
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

    def get_by_id(self, org_id: int, actor: User | None = None):
        """Get organization by ID with org isolation for non-admins."""
        org = self.repo.find_by_id(org_id)

        if actor and actor.organization_id is not None:
            if actor.organization_id != org.id:
                raise NotFoundError(f"Organization with ID {org_id} not found")

        return org

    def list_all(self, query, *, actor: User | None = None):
        """List organizations. Non-admin sees only own org."""
        if actor and actor.organization_id is not None:
            org = self.repo.get_by_id(actor.organization_id)
            return ([org] if org else [], 1 if org else 0)

        orgs = self.repo.list_all(skip=query.skip, limit=query.limit)
        count = self.repo.count()
        return orgs, count

    def create(self, request: OrganizationCreateRequest, *, actor: User):
        """Create organization."""
        try:
            if self.repo.get_by_name(request.name):
                raise ConflictError(f"Organization '{request.name}' already exists")
            org = self.repo.create(name=request.name)
            self.repo.flush()
            self.repo.refresh(org)
            self._record_audit("CREATE", org, actor, {}, self._state(org))
            self.repo.commit()
            return org
        except Exception:
            self.repo.rollback()
            raise

    def update(self, org_id: int, request: OrganizationUpdateRequest, actor: User):
        """Update organization."""
        try:
            org = self.get_by_id(org_id)
            old_state = self._state(org)
            if request.name is not None:
                existing = self.repo.get_by_name(request.name)
                if existing and existing.id != org.id:
                    raise ConflictError(f"Organization name already exists")
            self.repo.update(org, name=request.name)
            self.repo.flush()
            self.repo.refresh(org)
            new_state = self._state(org)
            if not calculate_delta(old_state, new_state):
                self.repo.commit(skip_audit=True)
                return org
            self._record_audit("UPDATE", org, actor, old_state, new_state)
            self.repo.commit()
            return org
        except Exception:
            self.repo.rollback()
            raise

    def delete(self, org_id: int, actor: User) -> None:
        """Delete organization."""
        try:
            org = self.get_by_id(org_id)
            old_state = self._state(org)
            self.repo.delete(org)
            self._record_audit("DELETE", org, actor, old_state, {})
            self.repo.commit()
        except IntegrityError as e:
            self.repo.rollback()
            raise ConflictError("Cannot delete organization with related objects")
        except Exception:
            self.repo.rollback()
            raise

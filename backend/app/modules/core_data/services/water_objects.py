"""Water object management service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.water_objects import (
    WaterObjectCreateRequest,
    WaterObjectUpdateRequest,
)
from app.modules.security.access import OrganizationAccess


class WaterObjectService:
    """Service for water object management operations."""

    def __init__(
        self,
        repo: WaterObjectRepository,
        org_repo: OrganizationRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.org_repo = org_repo
        self.audit = audit

    def _state(self, obj) -> dict:
        return {
            "name": obj.name,
            "object_type": obj.object_type,
            "organization_id": obj.organization_id,
            "is_active": obj.is_active,
        }

    def _record_audit(
        self,
        action: str,
        obj,
        org_access: OrganizationAccess,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_WATER_OBJECT.value,
                entity_id=str(obj.id),
                action=action,
                actor_id=str(org_access.actor.id),
                actor_display_name=org_access.actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, obj_id: UUID, organization_id: UUID | None = None):
        """Get water object by ID, optionally scoped to organization."""
        if organization_id is not None:
            return self.repo.find_in_organization(obj_id, organization_id)
        return self.repo.find_by_id(obj_id)

    def list_all(self, query, org_access: OrganizationAccess):
        """List water objects in organization."""
        objs = self.repo.list_all(
            organization_id=org_access.organization_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count(organization_id=org_access.organization_id)
        return objs, count

    def create(self, request: WaterObjectCreateRequest, org_access: OrganizationAccess):
        """Create water object in organization."""
        with self.repo.transaction():
            self.org_repo.find_by_id(
                org_access.organization_id
            )  # Validates org exists, raises NotFoundError if not
            obj = self.repo.create(
                organization_id=org_access.organization_id,
                name=request.name,
                object_type=request.object_type,
                location_description=request.location_description,
                latitude=request.latitude,
                longitude=request.longitude,
            )
            self.repo.flush()
            self.repo.refresh(obj)
            self._record_audit("CREATE", obj, org_access, {}, self._state(obj))
            return obj

    def update(
        self,
        obj_id: UUID,
        request: WaterObjectUpdateRequest,
        org_access: OrganizationAccess,
    ):
        """Update water object."""
        with self.repo.transaction() as tx:
            obj = self.repo.find_in_organization(obj_id, org_access.organization_id)
            old_state = self._state(obj)
            self.repo.update(obj, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(obj)
            new_state = self._state(obj)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return obj
            self._record_audit("UPDATE", obj, org_access, old_state, new_state)
            return obj

    def delete(self, obj_id: UUID, org_access: OrganizationAccess) -> None:
        """Delete water object."""
        try:
            with self.repo.transaction():
                obj = self.repo.find_in_organization(obj_id, org_access.organization_id)
                old_state = self._state(obj)
                self.repo.delete(obj)
                self._record_audit("DELETE", obj, org_access, old_state, {})
        except IntegrityError as err:
            raise ConflictError(
                "Cannot delete water object with related devices"
            ) from err

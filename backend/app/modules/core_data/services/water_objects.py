"""Water object management service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.water_objects import (
    WaterObjectCreateRequest,
    WaterObjectUpdateRequest,
)
from app.modules.core_data.utils.org_scope import (
    assert_same_organization,
    resolve_organization_id,
)


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
        self, action: str, obj, actor: User, old_state: dict, new_state: dict
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_WATER_OBJECT.value,
                entity_id=str(obj.id),
                action=action,
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, obj_id: UUID, actor: User):
        """Get water object by ID with org isolation."""
        obj = self.repo.find_by_id(obj_id)
        assert_same_organization(actor, obj.organization_id)
        return obj

    def list_all(self, query, *, actor: User = None):
        """List water objects with org isolation."""
        if actor and actor.organization_id is not None:
            org_id = (
                actor.organization_id
            )  # non-admin: wymuszone, ignoruje query.organization_id
        else:
            org_id = getattr(
                query, "organization_id", None
            )  # admin: z klienta; None = bez filtra
        objs = self.repo.list_all(
            organization_id=org_id, skip=query.skip, limit=query.limit
        )
        count = self.repo.count(organization_id=org_id)
        return objs, count

    def create(self, request: WaterObjectCreateRequest, *, actor: User):
        """Create water object."""
        try:
            org_id = resolve_organization_id(actor, request.organization_id)
            self.org_repo.find_by_id(org_id)
            obj = self.repo.create(
                organization_id=org_id,
                name=request.name,
                object_type=request.object_type,
                location_description=request.location_description,
                latitude=request.latitude,
                longitude=request.longitude,
            )
            self.repo.flush()
            self.repo.refresh(obj)
            self._record_audit("CREATE", obj, actor, {}, self._state(obj))
            self.repo.commit()
            return obj
        except Exception:
            self.repo.rollback()
            raise

    def update(self, obj_id: int, request: WaterObjectUpdateRequest, actor: User):
        """Update water object."""
        try:
            obj = self.get_by_id(obj_id, actor)
            old_state = self._state(obj)
            self.repo.update(obj, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(obj)
            new_state = self._state(obj)
            if not calculate_delta(old_state, new_state):
                self.repo.commit(skip_audit=True)
                return obj
            self._record_audit("UPDATE", obj, actor, old_state, new_state)
            self.repo.commit()
            return obj
        except Exception:
            self.repo.rollback()
            raise

    def delete(self, obj_id: int, actor: User) -> None:
        """Delete water object."""
        try:
            obj = self.get_by_id(obj_id, actor)
            old_state = self._state(obj)
            self.repo.delete(obj)
            self._record_audit("DELETE", obj, actor, old_state, {})
            self.repo.commit()
        except IntegrityError as err:
            self.repo.rollback()
            raise ConflictError(
                "Cannot delete water object with related devices"
            ) from err
        except Exception:
            self.repo.rollback()
            raise

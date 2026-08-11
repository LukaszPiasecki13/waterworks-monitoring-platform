"""Measurement point management service."""

from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError, NotFoundError
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.measurement_points import (
    MeasurementPointCreateRequest,
    MeasurementPointUpdateRequest,
)
from app.modules.core_data.utils.org_scope import assert_same_organization


class MeasurementPointService:
    """Service for measurement point management operations."""

    def __init__(
        self,
        repo: MeasurementPointRepository,
        device_repo: DeviceRepository,
        water_object_repo: WaterObjectRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.device_repo = device_repo
        self.water_object_repo = water_object_repo
        self.audit = audit

    def _state(self, point) -> dict:
        return {
            "device_id": point.device_id,
            "external_id": point.external_id,
            "point_type": point.point_type,
            "unit": point.unit,
            "is_active": point.is_active,
        }

    def _record_audit(self, action: str, point, actor: User, old_state: dict, new_state: dict) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_MEASUREMENT_POINT.value,
                entity_id=str(point.id),
                action=action,
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, point_id: UUID, actor: User):
        """Get measurement point by ID with org isolation."""
        point = self.repo.find_by_id(point_id)
        device = self.device_repo.get_by_id(point.device_id)
        if device:
            water_obj = self.water_object_repo.get_by_id(device.water_object_id)
            if water_obj:
                assert_same_organization(actor, water_obj.organization_id)
        return point

    def list_all(self, query, *, actor: User | None = None):
        """List measurement points with org isolation."""
        if actor and actor.organization_id is not None:
            org_id = actor.organization_id  # non-admin: wymuszone, ignoruje query.organization_id
        else:
            org_id = getattr(query, "organization_id", None)  # admin: z klienta; None = bez filtra

        if query.device_id is not None and org_id is not None:
            device = self.device_repo.get_by_id(query.device_id)
            if device:
                water_obj = self.water_object_repo.get_by_id(device.water_object_id)
                if water_obj and water_obj.organization_id != org_id:
                    raise NotFoundError("Device not found")

        points = self.repo.list_all_with_org_filter(
            organization_id=org_id,
            device_id=query.device_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count_with_org_filter(
            organization_id=org_id,
            device_id=query.device_id,
        )
        return points, count

    def create(self, request: MeasurementPointCreateRequest, *, actor: User):
        """Create measurement point."""
        try:
            device = self.device_repo.find_by_id(request.device_id)
            water_obj = self.water_object_repo.get_by_id(device.water_object_id)
            if water_obj:
                assert_same_organization(actor, water_obj.organization_id)
            existing = self.repo.get_by_device_and_external_id(
                request.device_id, request.external_id
            )
            if existing:
                raise ConflictError("Measurement point with this external_id already exists")
            point = self.repo.create(
                device_id=request.device_id,
                external_id=request.external_id,
                point_type=request.point_type,
                unit=request.unit,
                min_technical=request.min_technical,
                max_technical=request.max_technical,
            )
            self.repo.flush()
            self.repo.refresh(point)
            self._record_audit("CREATE", point, actor, {}, self._state(point))
            self.repo.commit()
            return point
        except Exception:
            self.repo.rollback()
            raise

    def update(self, point_id: int, request: MeasurementPointUpdateRequest, actor: User):
        """Update measurement point."""
        try:
            point = self.get_by_id(point_id, actor)
            old_state = self._state(point)
            self.repo.update(point, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(point)
            new_state = self._state(point)
            if not calculate_delta(old_state, new_state):
                self.repo.commit(skip_audit=True)
                return point
            self._record_audit("UPDATE", point, actor, old_state, new_state)
            self.repo.commit()
            return point
        except Exception:
            self.repo.rollback()
            raise

    def delete(self, point_id: int, actor: User) -> None:
        """Delete measurement point."""
        try:
            point = self.get_by_id(point_id, actor)
            old_state = self._state(point)
            self.repo.delete(point)
            self._record_audit("DELETE", point, actor, old_state, {})
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise

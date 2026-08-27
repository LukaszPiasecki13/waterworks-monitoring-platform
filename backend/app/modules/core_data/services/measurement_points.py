"""Measurement point management service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import BadRequestError, ConflictError
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.core_data.registry import SensorRegistry
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.schemas.measurement_points import (
    MeasurementPointCreateRequest,
    MeasurementPointUpdateRequest,
)
from app.modules.security.access import OrganizationAccess


class MeasurementPointService:
    """Service for measurement point management operations.

    Callers are expected to have already validated organization membership
    and permissions (see `require_org_access`) and pass in the resulting
    `OrganizationAccess`.
    """

    def __init__(
        self,
        repo: MeasurementPointRepository,
        device_repo: DeviceRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.device_repo = device_repo
        self.audit = audit

    def _state(self, point) -> dict:
        return {
            "device_id": point.device_id,
            "external_id": point.external_id,
            "point_type": point.point_type,
            "unit": point.unit,
            "is_active": point.is_active,
        }

    def _record_audit(
        self,
        action: str,
        point,
        org_access: OrganizationAccess,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_MEASUREMENT_POINT.value,
                entity_id=str(point.id),
                action=action,
                actor_id=str(org_access.actor.id),
                actor_display_name=org_access.actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, point_id: UUID, org_access: OrganizationAccess):
        """Get measurement point by ID."""
        return self.repo.find_in_organization(point_id, org_access.organization_id)

    def list_all(self, query, org_access: OrganizationAccess):
        """List measurement points in organization."""
        points = self.repo.list_all_with_org_filter(
            organization_id=org_access.organization_id,
            device_id=query.device_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count_with_org_filter(
            organization_id=org_access.organization_id,
            device_id=query.device_id,
        )
        return points, count

    def create(
        self, request: MeasurementPointCreateRequest, org_access: OrganizationAccess
    ):
        """Create measurement point in organization."""
        # Validate point_type against registry
        if not SensorRegistry.is_valid_point_type(request.point_type):
            raise BadRequestError(
                f"Unknown point_type: {request.point_type}. "
                f"Valid types: {', '.join(SensorRegistry.point_type_ids())}"
            )

        with self.repo.transaction():
            self.device_repo.find_in_organization(
                request.device_id, org_access.organization_id
            )
            existing = self.repo.get_by_device_and_external_id(
                request.device_id, request.external_id
            )
            if existing:
                raise ConflictError(
                    "Measurement point with this external_id already exists"
                )
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
            self._record_audit("CREATE", point, org_access, {}, self._state(point))
            return point

    def update(
        self,
        point_id: UUID,
        request: MeasurementPointUpdateRequest,
        org_access: OrganizationAccess,
    ):
        """Update measurement point."""
        # Validate point_type if provided
        if request.point_type and not SensorRegistry.is_valid_point_type(
            request.point_type
        ):
            raise BadRequestError(
                f"Unknown point_type: {request.point_type}. "
                f"Valid types: {', '.join(SensorRegistry.point_type_ids())}"
            )

        with self.repo.transaction() as tx:
            point = self.repo.find_in_organization(point_id, org_access.organization_id)
            old_state = self._state(point)
            self.repo.update(point, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(point)
            new_state = self._state(point)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return point
            self._record_audit("UPDATE", point, org_access, old_state, new_state)
            return point

    def delete(self, point_id: UUID, org_access: OrganizationAccess) -> None:
        """Delete measurement point."""
        with self.repo.transaction():
            point = self.repo.find_in_organization(point_id, org_access.organization_id)
            old_state = self._state(point)
            self.repo.delete(point)
            self._record_audit("DELETE", point, org_access, old_state, {})

    def get_or_create_internal(
        self, device_id: UUID, external_id: str, point_type: str, unit: str
    ) -> MeasurementPoint:
        """Get or create measurement point (auto-provisioning, no audit).

        Used for internal operations like firmware auto-provisioning when a new
        sensor is detected. Does not record audit trail.

        Must be called within an active transaction.
        """
        existing = self.repo.get_by_device_and_external_id(device_id, external_id)
        if existing:
            return existing

        try:
            point = MeasurementPoint(
                device_id=device_id,
                external_id=external_id,
                point_type=point_type,
                unit=unit,
                is_active=True,
            )
            self.repo.session.add(point)
            self.repo.flush()
        except IntegrityError:
            self.repo.session.rollback()
            existing = self.repo.get_by_device_and_external_id(device_id, external_id)
            if existing:
                return existing
            raise

        self.repo.refresh(point)
        return point

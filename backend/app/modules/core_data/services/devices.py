"""Device management service."""

import secrets
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError, NotFoundError
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.devices import (
    DeviceCreateRequest,
    DeviceCreateResponse,
    DeviceResponse,
    DeviceUpdateRequest,
)
from app.modules.core_data.utils.org_scope import assert_same_organization
from app.modules.security.services.password import hash_password, verify_password


class DeviceService:
    """Service for device management operations."""

    @staticmethod
    def generate_secret() -> str:
        """Generate a random device secret."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_secret(plain: str) -> str:
        """Hash device secret using bcrypt."""
        return hash_password(plain)

    @staticmethod
    def verify_secret(plain: str, hashed: str) -> bool:
        """Verify device secret against hash."""
        return verify_password(plain, hashed)

    def __init__(
        self,
        repo: DeviceRepository,
        water_object_repo: WaterObjectRepository,
        audit: AuditPort,
    ):
        self.repo = repo
        self.water_object_repo = water_object_repo
        self.audit = audit

    def _state(self, device) -> dict:
        return {
            "external_id": device.external_id,
            "water_object_id": device.water_object_id,
            "firmware_version": device.firmware_version,
            "is_active": device.is_active,
        }

    def _record_audit(
        self, action: str, device, actor: User, old_state: dict, new_state: dict
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_DEVICE.value,
                entity_id=str(device.id),
                action=action,
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, device_id: UUID, actor: User):
        """Get device by ID with org isolation."""
        device = self.repo.find_by_id(device_id)
        water_obj = self.water_object_repo.get_by_id(device.water_object_id)
        if water_obj:
            assert_same_organization(actor, water_obj.organization_id)
        return device

    def list_all(self, query, *, actor: User | None = None):
        """List devices with org isolation."""
        if actor and actor.organization_id is not None:
            org_id = actor.organization_id  # non-admin: wymuszone, ignoruje query.organization_id
        else:
            org_id = getattr(query, "organization_id", None)  # admin: z klienta; None = bez filtra

        if query.water_object_id is not None and org_id is not None:
            water_obj = self.water_object_repo.get_by_id(query.water_object_id)
            if water_obj and water_obj.organization_id != org_id:
                raise NotFoundError("Water object not found")

        devices = self.repo.list_all_with_org_filter(
            organization_id=org_id,
            water_object_id=query.water_object_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count_with_org_filter(
            organization_id=org_id,
            water_object_id=query.water_object_id,
        )
        return devices, count

    def create(
        self, request: DeviceCreateRequest, *, actor: User
    ) -> DeviceCreateResponse:
        """Create device, return response with plain_secret."""
        try:
            water_obj = self.water_object_repo.find_by_id(request.water_object_id)
            assert_same_organization(actor, water_obj.organization_id)
            if self.repo.get_by_external_id(request.external_id):
                raise ConflictError("Device with this external_id already exists")
            plain_secret = self.generate_secret()
            hashed_secret = self.hash_secret(plain_secret)
            device = self.repo.create(
                water_object_id=request.water_object_id,
                external_id=request.external_id,
                hashed_secret=hashed_secret,
                firmware_version=request.firmware_version,
            )
            self.repo.flush()
            self.repo.refresh(device)
            self._record_audit("CREATE", device, actor, {}, self._state(device))
            self.repo.commit()
            response = DeviceResponse.model_validate(device)
            return DeviceCreateResponse(
                **response.model_dump(), plain_secret=plain_secret
            )
        except Exception:
            self.repo.rollback()
            raise

    def update(self, device_id: int, request: DeviceUpdateRequest, actor: User):
        """Update device."""
        try:
            device = self.get_by_id(device_id, actor)
            old_state = self._state(device)
            self.repo.update(device, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(device)
            new_state = self._state(device)
            if not calculate_delta(old_state, new_state):
                self.repo.commit(skip_audit=True)
                return device
            self._record_audit("UPDATE", device, actor, old_state, new_state)
            self.repo.commit()
            return device
        except Exception:
            self.repo.rollback()
            raise

    def delete(self, device_id: UUID, actor: User) -> None:
        """Delete device."""
        try:
            device = self.get_by_id(device_id, actor)
            old_state = self._state(device)
            self.repo.delete(device)
            self._record_audit("DELETE", device, actor, old_state, {})
            self.repo.commit()
        except IntegrityError:
            self.repo.rollback()
            raise ConflictError("Cannot delete device with related measurement points")
        except Exception:
            self.repo.rollback()
            raise

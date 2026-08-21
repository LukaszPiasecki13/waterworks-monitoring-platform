"""Device management service."""

import secrets
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import ConflictError
from app.modules.core_data.models.device import Device
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.schemas.devices import (
    DeviceCreateRequest,
    DeviceUpdateRequest,
)
from app.modules.security.access import OrganizationAccess
from app.modules.security.services.password import hash_password, verify_password


class DeviceService:
    """Service for device management operations.

    Callers are expected to have already validated organization membership
    and permissions (see `require_org_access`) and pass in the resulting
    `OrganizationAccess`.
    """

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
        self,
        action: str,
        device,
        org_access: OrganizationAccess,
        old_state: dict,
        new_state: dict,
    ) -> None:
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_DEVICE.value,
                entity_id=str(device.id),
                action=action,
                actor_id=str(org_access.actor.id),
                actor_display_name=org_access.actor.email,
                changes=calculate_delta(old_state, new_state),
            )
        )

    def get_by_id(self, device_id: UUID, org_access: OrganizationAccess):
        """Get device by ID."""
        return self.repo.find_in_organization(device_id, org_access.organization_id)

    def get_by_external_id(self, external_id: str) -> Device | None:
        """Get device by external ID, returns None if not found."""
        return self.repo.get_by_external_id(external_id)

    def list_all(self, query, org_access: OrganizationAccess):
        """List devices in organization."""
        devices = self.repo.list_all_with_org_filter(
            organization_id=org_access.organization_id,
            water_object_id=query.water_object_id,
            skip=query.skip,
            limit=query.limit,
        )
        count = self.repo.count_with_org_filter(
            organization_id=org_access.organization_id,
            water_object_id=query.water_object_id,
        )
        return devices, count

    def create(
        self, request: DeviceCreateRequest, org_access: OrganizationAccess
    ) -> Device:
        """Create device in organization.

        Generates a per-device secret, hashes and stores it. Returns the plaintext
        secret to the operator (only shown at creation time) so they can configure
        the device to authenticate to ingest service.
        """
        with self.repo.transaction():
            self.water_object_repo.find_in_organization(
                request.water_object_id, org_access.organization_id
            )
            if self.repo.get_by_external_id(request.external_id):
                raise ConflictError("Device with this external_id already exists")
            plaintext_secret = self.generate_secret()
            hashed_secret = self.hash_secret(plaintext_secret)
            device = self.repo.create(
                water_object_id=request.water_object_id,
                external_id=request.external_id,
                hashed_secret=hashed_secret,
                firmware_version=request.firmware_version,
            )
            self.repo.flush()
            self.repo.refresh(device)
            # Attach plaintext secret to device object for inclusion in response
            device.secret = plaintext_secret
            self._record_audit("CREATE", device, org_access, {}, self._state(device))
            return device

    def update(
        self,
        device_id: UUID,
        request: DeviceUpdateRequest,
        org_access: OrganizationAccess,
    ):
        """Update device."""
        with self.repo.transaction() as tx:
            device = self.repo.find_in_organization(
                device_id, org_access.organization_id
            )
            old_state = self._state(device)
            self.repo.update(device, **request.model_dump(exclude_unset=True))
            self.repo.flush()
            self.repo.refresh(device)
            new_state = self._state(device)
            if not calculate_delta(old_state, new_state):
                tx.skip_audit()
                return device
            self._record_audit("UPDATE", device, org_access, old_state, new_state)
            return device

    def delete(self, device_id: UUID, org_access: OrganizationAccess) -> None:
        """Delete device."""
        try:
            with self.repo.transaction():
                device = self.repo.find_in_organization(
                    device_id, org_access.organization_id
                )
                old_state = self._state(device)
                self.repo.delete(device)
                self._record_audit("DELETE", device, org_access, old_state, {})
        except IntegrityError as err:
            raise ConflictError(
                "Cannot delete device with related measurement points"
            ) from err

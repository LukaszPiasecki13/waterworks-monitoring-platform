"""Integration tests for device lifecycle — detach vs complete deletion."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.modules.core_data.models import (
    Device,
    Organization,
    User,
    WaterObject,
)
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.services.device_lifecycle import DeviceLifecycleService
from app.modules.core_data.services.devices import DeviceService
from app.modules.device_identity.models.device_activation_code import (
    DeviceActivationCode,
)
from app.modules.device_identity.models.device_credential import DeviceCredential
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.telemetry.repositories.packets import TelemetryPacketRepository
from app.modules.telemetry.services.ingest import TelemetryIngestService


class TestDeviceLifecycle:
    """Integration tests for device lifecycle scenarios."""

    def test_detach_makes_device_available_for_reassignment(
        self, db_session: Session
    ) -> None:
        """After detach, device should be reassignable to another org."""
        # Setup: create org A and device assigned to it
        org_a = Organization(id=uuid4(), name="OrgA")
        db_session.add(org_a)
        db_session.flush()

        water_obj_a = WaterObject(
            id=uuid4(),
            organization_id=org_a.id,
            name="WaterObjA",
            object_type="pump_station",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(water_obj_a)
        db_session.flush()

        credential = DeviceCredential(
            id=uuid4(),
            serial_number="device-detach-reassign",
            public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            status="claimed",
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(credential)
        db_session.flush()

        device = Device(
            id=uuid4(),
            water_object_id=water_obj_a.id,
            external_id="device-detach-reassign",
            device_credential_id=credential.id,
            firmware_version="1.0",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(device)
        db_session.commit()

        # Detach from org A
        device_repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        device_service = DeviceService(device_repo, water_obj_repo, MagicMock())

        admin = User(
            id=uuid4(),
            username=f"admin_{uuid4().hex[:8]}",
            email=f"admin_{uuid4().hex[:8]}@example.com",
            hashed_password="hash",
            first_name="Admin",
            last_name="Test",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(admin)
        db_session.commit()

        from app.modules.security.access import OrganizationAccess

        context_a = OrganizationAccess(
            actor=admin,
            organization_id=org_a.id,
            permissions={"CAN_MANAGE_ASSETS"},
        )

        device_service.detach_from_organization(device.id, context_a)
        db_session.commit()

        # Verify device has no water object
        db_session.refresh(device)
        assert device.water_object_id is None

        # Setup: create org B and water object
        org_b = Organization(id=uuid4(), name="OrgB")
        db_session.add(org_b)
        db_session.flush()

        water_obj_b = WaterObject(
            id=uuid4(),
            organization_id=org_b.id,
            name="WaterObjB",
            object_type="pump_station",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(water_obj_b)
        db_session.commit()

        # Reassign device to org B
        device_service.assign_water_object(
            external_id="device-detach-reassign",
            water_object_id=water_obj_b.id,
            actor_id=str(admin.id),
            actor_display_name=admin.email,
            context_id=org_b.id,
        )
        db_session.commit()

        # Verify reassignment succeeded
        db_session.refresh(device)
        assert device.water_object_id == water_obj_b.id

    def test_complete_deletion_removes_activation_code_reference(
        self, db_session: Session
    ) -> None:
        """After deletion, activation_code.redeemed_by_credential_id becomes NULL."""
        # Setup: create credential, device, and activation code
        admin = User(
            id=uuid4(),
            username=f"admin_{uuid4().hex[:8]}",
            email=f"admin_{uuid4().hex[:8]}@example.com",
            hashed_password="hash",
            first_name="Admin",
            last_name="Test",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(admin)
        db_session.flush()

        credential = DeviceCredential(
            id=uuid4(),
            serial_number="device-with-activation-code",
            public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            status="claimed",
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(credential)
        db_session.flush()

        activation_code = DeviceActivationCode(
            id=uuid4(),
            code_hash="test_hash_123",
            status="redeemed",
            expires_at=datetime(2026, 12, 31),
            used_at=datetime(2026, 1, 1),
            redeemed_by_credential_id=credential.id,
            created_by_user_id=admin.id,
            created_at=datetime(2026, 1, 1),
        )
        db_session.add(activation_code)
        db_session.flush()

        org = Organization(id=uuid4(), name="OrgTest")
        db_session.add(org)
        db_session.flush()

        water_obj = WaterObject(
            id=uuid4(),
            organization_id=org.id,
            name="WaterObj",
            object_type="pump_station",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(water_obj)
        db_session.flush()

        device = Device(
            id=uuid4(),
            water_object_id=water_obj.id,
            external_id="device-with-activation-code",
            device_credential_id=credential.id,
            firmware_version="1.0",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(device)
        db_session.commit()

        # Execute complete deletion
        device_repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        credential_repo = DeviceCredentialRepository(db_session)
        telemetry_packet_repo = TelemetryPacketRepository(db_session)
        device_service = DeviceService(device_repo, water_obj_repo, MagicMock())
        telemetry_service = TelemetryIngestService(telemetry_packet_repo)
        lifecycle_service = DeviceLifecycleService(
            device_service, credential_repo, telemetry_service, MagicMock()
        )

        lifecycle_service.delete_device_completely(
            device.id,
            actor_id="platform-admin",
            actor_display_name="Platform Admin",
        )
        db_session.commit()

        # Verify activation code still exists but reference is NULL
        db_session.refresh(activation_code)
        assert activation_code.redeemed_by_credential_id is None
        assert activation_code.code_hash == "test_hash_123"

    def test_complete_deletion_is_atomic_rollback_on_failure(
        self, db_session: Session
    ) -> None:
        """If any step fails, entire transaction should rollback."""
        device, _ = self._setup_device_with_credential_and_telemetry(db_session)
        original_credential_id = device.device_credential_id

        device_repo = DeviceRepository(db_session)
        water_obj_repo = WaterObjectRepository(db_session)
        credential_repo = DeviceCredentialRepository(db_session)
        telemetry_packet_repo = TelemetryPacketRepository(db_session)
        device_service = DeviceService(device_repo, water_obj_repo, MagicMock())
        telemetry_service = TelemetryIngestService(telemetry_packet_repo)

        audit_mock = MagicMock(spec=AuditPort)
        lifecycle_service = DeviceLifecycleService(
            device_service, credential_repo, telemetry_service, audit_mock
        )

        # Patch credential_repo.delete to raise an error
        with (
            patch.object(credential_repo, "delete", side_effect=Exception("DB error")),
            pytest.raises(Exception, match="DB error"),
        ):
            lifecycle_service.delete_device_completely(
                device.id,
                actor_id="platform-admin",
                actor_display_name="Platform Admin",
            )

        # Verify device still exists (rollback happened)
        db_session.rollback()  # reset session state
        device_count = db_session.query(Device).filter_by(id=device.id).count()
        assert device_count == 1

        # Verify credential still exists
        credential_count = (
            db_session.query(DeviceCredential)
            .filter_by(id=original_credential_id)
            .count()
        )
        assert credential_count == 1

    def _setup_device_with_credential_and_telemetry(
        self, db_session: Session
    ) -> tuple[Device, TelemetryPacket]:
        """Helper: create device with credential and telemetry packet."""
        org = Organization(id=uuid4(), name="OrgTest")
        db_session.add(org)
        db_session.flush()

        water_obj = WaterObject(
            id=uuid4(),
            organization_id=org.id,
            name="WaterObj",
            object_type="pump_station",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(water_obj)
        db_session.flush()

        credential = DeviceCredential(
            id=uuid4(),
            serial_number="device-test-lifecycle",
            public_key_pem="-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
            status="claimed",
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(credential)
        db_session.flush()

        device = Device(
            id=uuid4(),
            water_object_id=water_obj.id,
            external_id="device-test-lifecycle",
            device_credential_id=credential.id,
            firmware_version="1.0",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        db_session.add(device)
        db_session.flush()

        packet = TelemetryPacket(
            id=uuid4(),
            device_id="device-test-lifecycle",
            seq=1,
            sent_at=datetime(2026, 1, 1),
            received_at=datetime(2026, 1, 1),
            payload={"pressure": 1.5},
        )
        db_session.add(packet)
        db_session.commit()

        return device, packet

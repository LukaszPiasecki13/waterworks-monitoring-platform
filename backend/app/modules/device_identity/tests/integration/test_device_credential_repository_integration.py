"""Integration tests for DeviceCredentialRepository with real database.

These tests verify the repository actually works against the database,
including verifying that all required tables exist (via Alembic migrations).
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)


class TestDeviceCredentialRepositoryIntegration:
    """Integration tests against real database."""

    def test_repository_can_create_and_retrieve_credential(
        self, db_session: Session
    ) -> None:
        """Test repository creates and retrieves credentials from real database.

        This test verifies:
        1. device_credentials table exists (via migration)
        2. Repository can be instantiated without TypeError
        3. Repository can create and retrieve from database
        """
        repo = DeviceCredentialRepository(db_session)
        serial = f"TEST-SN-{uuid4().hex[:8]}"
        public_key = "-----BEGIN PUBLIC KEY-----\ntest-key\n-----END PUBLIC KEY-----"

        # Create
        repo.create(
            serial_number=serial,
            public_key_pem=public_key,
            status="unclaimed",
        )
        db_session.commit()

        # Verify it's persisted
        retrieved = repo.get_by_serial_number(serial)
        assert retrieved is not None
        assert retrieved.serial_number == serial
        assert retrieved.public_key_pem == public_key
        assert retrieved.status == "unclaimed"

    def test_find_by_serial_number_missing_device(self, db_session: Session) -> None:
        """Test find_by_serial_number raises NotFoundError for missing device."""
        repo = DeviceCredentialRepository(db_session)

        with pytest.raises(NotFoundError):
            repo.find_by_serial_number("NONEXISTENT-SN-12345")

    def test_repository_updates_challenge(self, db_session: Session) -> None:
        """Test repository can update pending challenge."""
        repo = DeviceCredentialRepository(db_session)
        serial = f"TEST-SN-{uuid4().hex[:8]}"
        public_key = "-----BEGIN PUBLIC KEY-----\ntest-key\n-----END PUBLIC KEY-----"

        # Create credential
        credential = repo.create(
            serial_number=serial,
            public_key_pem=public_key,
            status="unclaimed",
        )
        db_session.commit()

        # Update challenge
        challenge = f"challenge-{uuid4().hex}"
        credential.pending_challenge = challenge
        credential.challenge_expires_at = datetime.now(UTC)
        db_session.commit()

        # Verify update persisted
        retrieved = repo.get_by_serial_number(serial)
        assert retrieved.pending_challenge == challenge
        assert retrieved.challenge_expires_at is not None

    def test_repository_updates_status(self, db_session: Session) -> None:
        """Test repository can update credential status."""
        repo = DeviceCredentialRepository(db_session)
        serial = f"TEST-SN-{uuid4().hex[:8]}"
        public_key = "-----BEGIN PUBLIC KEY-----\ntest-key\n-----END PUBLIC KEY-----"

        # Create as unclaimed
        credential = repo.create(
            serial_number=serial,
            public_key_pem=public_key,
            status="unclaimed",
        )
        db_session.commit()

        # Update to claimed
        device_id = uuid4()
        credential.status = "claimed"
        credential.claimed_device_id = device_id
        credential.claimed_at = datetime.now(UTC)
        db_session.commit()

        # Verify update persisted
        retrieved = repo.get_by_serial_number(serial)
        assert retrieved.status == "claimed"
        assert retrieved.claimed_device_id == device_id
        assert retrieved.claimed_at is not None

    def test_unique_constraint_on_serial_number(self, db_session: Session) -> None:
        """Test serial_number unique constraint is enforced."""
        from sqlalchemy.exc import IntegrityError

        repo = DeviceCredentialRepository(db_session)
        serial = f"TEST-SN-{uuid4().hex[:8]}"
        public_key = "-----BEGIN PUBLIC KEY-----\ntest-key\n-----END PUBLIC KEY-----"

        # Create first credential
        repo.create(
            serial_number=serial,
            public_key_pem=public_key,
            status="unclaimed",
        )
        db_session.commit()

        # Try to create duplicate - should fail
        repo.create(
            serial_number=serial,
            public_key_pem=public_key,
            status="unclaimed",
        )

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_repository_with_dependency_injection(self, db_session: Session) -> None:
        """Test repository instantiation via dependency injection.

        This simulates how FastAPI endpoints use the repository.
        """
        from app.modules.device_identity.dependencies import (
            get_credential_repo,
        )

        repo = get_credential_repo(db_session)

        assert repo is not None
        assert isinstance(repo, DeviceCredentialRepository)
        assert repo.session == db_session

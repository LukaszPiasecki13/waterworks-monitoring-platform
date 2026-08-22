"""Integration tests for DeviceCredentialRepository."""

import pytest

from app.core.errors import NotFoundError
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)


class TestDeviceCredentialRepository:
    """Test repository instantiation and basic operations."""

    def test_repository_initialization(self, db_session):
        """Test repository can be instantiated without TypeError."""
        # This test verifies the fix for the TypeError:
        # SQLRepository.__init__() takes 2 positional arguments but 3 were given
        repo = DeviceCredentialRepository(db_session)
        assert repo.session == db_session

    def test_create_credential(self, db_session, test_serial_number, ec_key_pair):
        """Test creating a device credential."""
        repo = DeviceCredentialRepository(db_session)

        credential = repo.create(
            serial_number=test_serial_number,
            public_key_pem=ec_key_pair["public_pem"],
            status="unclaimed",
        )

        assert credential.serial_number == test_serial_number
        assert credential.public_key_pem == ec_key_pair["public_pem"]
        assert credential.status == "unclaimed"

    def test_get_by_serial_number_found(
        self, db_session, test_serial_number, ec_key_pair
    ):
        """Test retrieving credential by serial number."""
        repo = DeviceCredentialRepository(db_session)

        # Create a credential
        repo.create(
            serial_number=test_serial_number,
            public_key_pem=ec_key_pair["public_pem"],
            status="unclaimed",
        )
        db_session.commit()

        # Retrieve it
        credential = repo.get_by_serial_number(test_serial_number)

        assert credential is not None
        assert credential.serial_number == test_serial_number

    def test_get_by_serial_number_not_found(self, db_session):
        """Test retrieving non-existent credential returns None."""
        repo = DeviceCredentialRepository(db_session)

        credential = repo.get_by_serial_number("NONEXISTENT-SN")

        assert credential is None

    def test_find_by_serial_number_found(
        self, db_session, test_serial_number, ec_key_pair
    ):
        """Test find_by_serial_number retrieves existing credential."""
        repo = DeviceCredentialRepository(db_session)

        # Create a credential
        repo.create(
            serial_number=test_serial_number,
            public_key_pem=ec_key_pair["public_pem"],
            status="unclaimed",
        )
        db_session.commit()

        # Retrieve it
        credential = repo.find_by_serial_number(test_serial_number)

        assert credential is not None
        assert credential.serial_number == test_serial_number

    def test_find_by_serial_number_not_found(self, db_session):
        """Test find_by_serial_number raises NotFoundError."""
        repo = DeviceCredentialRepository(db_session)

        with pytest.raises(NotFoundError):
            repo.find_by_serial_number("NONEXISTENT-SN")

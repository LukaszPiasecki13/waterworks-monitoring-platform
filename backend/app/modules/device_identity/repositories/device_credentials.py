"""Repository for device credentials."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.sql.repository import SQLRepository
from app.modules.device_identity.models.device_credential import DeviceCredential


class DeviceCredentialRepository(SQLRepository):
    """Manage device credentials in the database."""

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_serial_number(self, serial_number: str) -> DeviceCredential | None:
        """Get a credential by serial number, return None if not found."""
        stmt = select(DeviceCredential).where(
            DeviceCredential.serial_number == serial_number
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_by_serial_number(self, serial_number: str) -> DeviceCredential:
        """Get a credential by serial number, raise NotFoundError if not found."""
        credential = self.get_by_serial_number(serial_number)
        if not credential:
            from app.core.errors import NotFoundError

            raise NotFoundError(f"Device credential not found: {serial_number}")
        return credential

    def create(
        self,
        serial_number: str,
        public_key_pem: str,
        status: str = "unclaimed",
    ) -> DeviceCredential:
        """Create a new device credential."""
        credential = DeviceCredential(
            serial_number=serial_number,
            public_key_pem=public_key_pem,
            status=status,
        )
        self.session.add(credential)
        return credential

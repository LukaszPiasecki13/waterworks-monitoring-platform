"""Repository for DeviceActivationCode model database operations."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.device_identity.models.device_activation_code import (
    DeviceActivationCode,
)


class DeviceActivationCodeRepository(SQLRepository):
    """Repository for DeviceActivationCode model database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self, code_hash: str, expires_at: datetime, created_by_user_id: UUID
    ) -> DeviceActivationCode:
        """Create new activation code."""
        code = DeviceActivationCode(
            code_hash=code_hash,
            expires_at=expires_at,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(code)
        return code

    def get_by_id(self, code_id: UUID) -> DeviceActivationCode | None:
        """Get activation code by ID."""
        return (
            self.session.query(DeviceActivationCode)
            .filter(DeviceActivationCode.id == code_id)
            .first()
        )

    def find_by_id(self, code_id: UUID) -> DeviceActivationCode:
        """Find activation code by ID or raise NotFoundError."""
        code = self.get_by_id(code_id)
        if not code:
            raise NotFoundError("Activation code not found")
        return code

    def get_by_code_hash(self, code_hash: str) -> DeviceActivationCode | None:
        """Get activation code by hash."""
        return (
            self.session.query(DeviceActivationCode)
            .filter(DeviceActivationCode.code_hash == code_hash)
            .first()
        )

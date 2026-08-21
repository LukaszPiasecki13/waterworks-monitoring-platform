"""Request and response schemas for permissions."""

from uuid import UUID

from pydantic import ConfigDict

from app.core.schemas import BaseSchema


class PermissionResponse(BaseSchema):
    id: UUID
    code: str
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class MyPermissionsResponse(BaseSchema):
    permissions: list[str]
    group_ids: list[UUID]

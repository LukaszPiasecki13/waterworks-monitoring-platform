"""Request and response schemas for permissions and user groups."""

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.core.schemas import BaseSchema


class PermissionResponse(BaseSchema):
    id: UUID
    code: str
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class UserGroupCreateRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    permission_codes: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nazwa grupy nie może być pusta")
        return value


class UserGroupUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Nazwa grupy nie może być pusta")
        return value


class UserGroupSaveRequest(UserGroupCreateRequest):
    """Complete editable group state saved in one transaction."""

    user_ids: list[UUID] = Field(default_factory=list)


class PermissionCodesRequest(BaseSchema):
    permission_codes: list[str]


class UserIdsRequest(BaseSchema):
    user_ids: list[UUID]


class GroupIdsRequest(BaseSchema):
    group_ids: list[UUID]


class UserGroupResponse(BaseSchema):
    id: UUID
    name: str
    description: str
    is_system: bool
    system_key: str | None
    permissions: list[PermissionResponse]
    user_ids: list[UUID]
    created_at: datetime
    updated_at: datetime


class MyPermissionsResponse(BaseSchema):
    permissions: list[str]
    group_ids: list[UUID]

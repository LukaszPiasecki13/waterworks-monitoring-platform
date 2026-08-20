"""User context schemas — environments and permissions."""

from uuid import UUID

from pydantic import BaseModel


class OrganizationEnvironment(BaseModel):
    """Organization context: ID, name, and user's permissions in it."""

    organization_id: UUID
    organization_name: str
    permissions: list[str]


class PlatformEnvironment(BaseModel):
    """Platform-level context: user's global (super admin) permissions."""

    permissions: list[str]


class UserContextResponse(BaseModel):
    """Complete user access context: all organizations + platform permissions."""

    organizations: list[OrganizationEnvironment]
    platform: PlatformEnvironment | None

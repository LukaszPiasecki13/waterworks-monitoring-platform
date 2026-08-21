"""Organization membership API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.modules.core_data.dependencies import get_members_service
from app.modules.core_data.schemas.users import (
    ListMembersRequest,
    PaginatedResponse,
    UserResponse,
)
from app.modules.core_data.services.members import MembersService
from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import require_org_or_platform_permission
from app.modules.security.permission_catalog import (
    PLATFORM_MANAGE_MEMBERSHIPS,
    PLATFORM_VIEW_USERS,
)

router = APIRouter(prefix="/orgs/{org_id}/members", tags=["organization-members"])

require_member_access = require_org_or_platform_permission(
    PLATFORM_VIEW_USERS, PLATFORM_MANAGE_MEMBERSHIPS
)


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_members(
    org_id: UUID = Path(...),
    query: ListMembersRequest = Depends(),
    org_access: OrganizationAccess = Depends(require_member_access),
    service: MembersService = Depends(get_members_service),
):
    """List members of the organization (organization member or platform admin)."""
    members, total = service.list_members(org_access, query.skip, query.limit)
    return PaginatedResponse(
        items=members, total=total, skip=query.skip, limit=query.limit
    )


@router.post("/{user_id}", response_model=UserResponse)
def add_member(
    org_id: UUID = Path(...),
    user_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_member_access),
    service: MembersService = Depends(get_members_service),
):
    """Add an existing platform user as a member of the organization."""
    return service.add_member(user_id, org_access)


@router.delete("/{user_id}", status_code=204)
def remove_member(
    org_id: UUID = Path(...),
    user_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_member_access),
    service: MembersService = Depends(get_members_service),
):
    """Remove a member from the organization."""
    service.remove_member(user_id, org_access)

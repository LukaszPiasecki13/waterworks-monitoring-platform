"""Organization and platform security groups API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Response, status

from app.modules.security.access import OrganizationAccess, PlatformContext
from app.modules.security.dependencies import (
    get_group_service,
    require_org_or_platform_permission,
    require_platform_permission,
)
from app.modules.security.permission_catalog import (
    PLATFORM_MANAGE_ORGANIZATIONS,
)
from app.modules.security.schemas.groups import (
    UserGroupCreateRequest,
    UserGroupResponse,
    UserGroupSaveRequest,
    UserIdsRequest,
)
from app.modules.security.services.groups import GroupService

# Organization-scoped router
org_router = APIRouter(prefix="/orgs/{org_id}/groups", tags=["organization-groups"])

# Platform-scoped router
platform_router = APIRouter(prefix="/groups", tags=["platform-groups"])


# Organization-scoped endpoints
# Pattern: org member OR platform admin. Service checks CAN_VIEW_SECURITY /
# CAN_MANAGE_SECURITY.
require_org_group_access = require_org_or_platform_permission(
    PLATFORM_MANAGE_ORGANIZATIONS
)


@org_router.get("", response_model=list[UserGroupResponse])
def list_org_groups(
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_group_access),
    service: GroupService = Depends(get_group_service),
):
    """List security groups for this organization."""
    return service.list_org_groups(org_id)


@org_router.post(
    "", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED
)
def create_org_group(
    request: UserGroupCreateRequest,
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_group_access),
    service: GroupService = Depends(get_group_service),
):
    """Create a security group scoped to this organization."""
    return service.create_group(request, actor=org_access.actor, organization_id=org_id)


@org_router.put("/{group_id}", response_model=UserGroupResponse)
def save_org_group(
    group_id: UUID,
    request: UserGroupSaveRequest,
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_group_access),
    service: GroupService = Depends(get_group_service),
):
    """Save (name, description, permissions, members) an org group atomically."""
    service.get_org_group(group_id, org_id)
    return service.save_group(group_id, request, actor=org_access.actor)


@org_router.put("/{group_id}/users", response_model=UserGroupResponse)
def replace_org_group_users(
    group_id: UUID,
    request: UserIdsRequest,
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_group_access),
    service: GroupService = Depends(get_group_service),
):
    """Replace the member set of an organization group."""
    service.get_org_group(group_id, org_id)
    return service.replace_group_users(
        group_id, request.user_ids, actor=org_access.actor
    )


@org_router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org_group(
    group_id: UUID,
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_group_access),
    service: GroupService = Depends(get_group_service),
):
    """Delete a custom org group (system groups are rejected by the service)."""
    service.get_org_group(group_id, org_id)
    service.delete_group(group_id, actor=org_access.actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Platform-scoped endpoints


@platform_router.get("", response_model=list[UserGroupResponse])
def list_platform_groups(
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: GroupService = Depends(get_group_service),
):
    """List all security groups in the system (platform + organizational)."""
    return service.list_groups()


@platform_router.post(
    "", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED
)
def create_platform_group(
    request: UserGroupCreateRequest,
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: GroupService = Depends(get_group_service),
):
    """Create a platform-level security group."""
    return service.create_group(request, actor=context.actor, organization_id=None)


@platform_router.put("/{group_id}", response_model=UserGroupResponse)
def save_platform_group(
    group_id: UUID,
    request: UserGroupSaveRequest,
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: GroupService = Depends(get_group_service),
):
    """Save (name, description, permissions, members) a platform group atomically."""
    return service.save_group(group_id, request, actor=context.actor)


@platform_router.put("/{group_id}/users", response_model=UserGroupResponse)
def replace_platform_group_users(
    group_id: UUID,
    request: UserIdsRequest,
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: GroupService = Depends(get_group_service),
):
    """Replace the member set of a platform group."""
    return service.replace_group_users(group_id, request.user_ids, actor=context.actor)


@platform_router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_platform_group(
    group_id: UUID,
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: GroupService = Depends(get_group_service),
):
    """Delete a custom platform group (system groups are rejected by the service)."""
    service.delete_group(group_id, actor=context.actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

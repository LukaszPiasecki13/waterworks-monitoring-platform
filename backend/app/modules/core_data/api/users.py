"""Admin users API endpoints (platform-level)."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.audit import AuditReaderPort, EntityType
from app.modules.audit.dependencies import get_audit_reader
from app.modules.audit.schemas import AuditEventResponse, AuditHistoryQuery
from app.modules.core_data.dependencies import get_members_service, get_user_service
from app.modules.core_data.schemas.users import (
    ListUsersRequest,
    PaginatedResponse,
    UserCreateRequest,
    UserOrganizationsResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.modules.core_data.services.members import MembersService
from app.modules.core_data.services.users import UserService
from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import (
    require_platform_permission,
)
from app.modules.security.permission_catalog import (
    PLATFORM_MANAGE_USERS,
    PLATFORM_VIEW_USERS,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
)
def list_users(
    query: ListUsersRequest = Depends(),
    service: UserService = Depends(get_user_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_VIEW_USERS)
    ),
):
    """List users with optional filters."""
    users, total = service.list_users(query, actor=context.actor)
    return PaginatedResponse(
        items=users,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post(
    "",
    response_model=UserResponse,
)
def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_USERS)
    ),
):
    """Create new user."""
    return service.create_user(request, actor=context.actor)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_VIEW_USERS)
    ),
):
    """Get user by ID."""
    return service.get_user_by_id(user_id, actor=context.actor)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_USERS)
    ),
):
    """Update user."""
    return service.update_user(user_id, request, actor=context.actor)


@router.delete(
    "/{user_id}",
)
def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_USERS)
    ),
):
    """Delete user."""
    service.delete_user(user_id, actor=context.actor)
    return {"message": "User deleted successfully"}


@router.get(
    "/{user_id}/audit",
    response_model=list[AuditEventResponse],
)
def user_audit_history(
    user_id: UUID,
    query: AuditHistoryQuery = Depends(),
    service: UserService = Depends(get_user_service),
    audit: AuditReaderPort = Depends(get_audit_reader),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_VIEW_USERS)
    ),
):
    service.get_user_by_id(user_id, actor=context.actor)
    return audit.get_logs_for_entity(
        EntityType.CORE_DATA_USER.value,
        str(user_id),
        limit=query.limit,
        offset=query.offset,
    )


@router.get(
    "/{user_id}/organizations",
    response_model=UserOrganizationsResponse,
)
def get_user_organizations(
    user_id: UUID,
    service: MembersService = Depends(get_members_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_VIEW_USERS)
    ),
):
    """List organizations the user belongs to."""
    organizations = service.get_organizations_for_user(user_id)
    return UserOrganizationsResponse(organizations=organizations)


@router.post(
    "/{user_id}/organizations/{org_id}",
    status_code=204,
)
def assign_user_organization(
    user_id: UUID,
    org_id: UUID,
    service: MembersService = Depends(get_members_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_USERS)
    ),
):
    """Assign a user to an organization."""
    service.assign_user_to_organization(user_id, org_id, actor=context.actor)


@router.delete(
    "/{user_id}/organizations/{org_id}",
    status_code=204,
)
def remove_user_organization(
    user_id: UUID,
    org_id: UUID,
    service: MembersService = Depends(get_members_service),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_USERS)
    ),
):
    """Remove a user from an organization."""
    service.remove_user_from_organization(user_id, org_id, actor=context.actor)

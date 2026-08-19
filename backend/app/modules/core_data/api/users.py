"""Admin users API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.audit import AuditReaderPort, EntityType
from app.modules.audit.dependencies import get_audit_reader
from app.modules.audit.schemas import AuditEventResponse, AuditHistoryQuery
from app.modules.core_data.dependencies import get_user_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.users import (
    ListUsersRequest,
    PaginatedResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.modules.core_data.services.users import UserService
from app.modules.security.dependencies import (
    get_current_user,
    require_any_permission,
    require_permission,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_USERS,
    CAN_VIEW_SECURITY,
    CAN_VIEW_USERS,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    dependencies=[Depends(require_any_permission(CAN_VIEW_USERS, CAN_VIEW_SECURITY))],
)
def list_users(
    query: ListUsersRequest = Depends(),
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
):
    """List users with optional filters."""
    users, total = service.list_users(query, actor=user)
    return PaginatedResponse(
        items=users,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(CAN_MANAGE_USERS))],
)
def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
):
    """Create new user."""
    return service.create_user(request, actor=user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_any_permission(CAN_VIEW_USERS, CAN_VIEW_SECURITY))],
)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
):
    """Get user by ID."""
    return service.get_user_by_id(user_id, actor=user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(CAN_MANAGE_USERS))],
)
def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
):
    """Update user."""
    return service.update_user(user_id, request, actor=user)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permission(CAN_MANAGE_USERS))],
)
def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    admin: User = Depends(get_current_user),
):
    """Delete user."""
    service.delete_user(user_id, actor=admin)
    return {"message": "User deleted successfully"}


@router.get(
    "/{user_id}/audit",
    response_model=list[AuditEventResponse],
    dependencies=[Depends(require_any_permission(CAN_VIEW_USERS, CAN_VIEW_SECURITY))],
)
def user_audit_history(
    user_id: UUID,
    query: AuditHistoryQuery = Depends(),
    service: UserService = Depends(get_user_service),
    audit: AuditReaderPort = Depends(get_audit_reader),
    user: User = Depends(get_current_user),
):
    service.get_user_by_id(user_id, actor=user)
    return audit.get_logs_for_entity(
        EntityType.CORE_DATA_USER.value,
        str(user_id),
        limit=query.limit,
        offset=query.offset,
    )

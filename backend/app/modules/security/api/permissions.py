"""API for the permission catalog and user security groups."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.core.audit import AuditReaderPort, EntityType
from app.modules.audit.dependencies import get_audit_reader
from app.modules.audit.schemas import AuditEventResponse, AuditHistoryQuery
from app.modules.core_data.models import User
from app.modules.security.dependencies import (
    get_current_user,
    get_permission_service,
    require_permission,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_SECURITY,
    CAN_VIEW_SECURITY,
)
from app.modules.security.schemas import (
    GroupIdsRequest,
    MyPermissionsResponse,
    PermissionCodesRequest,
    PermissionResponse,
    UserGroupCreateRequest,
    UserGroupResponse,
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
    UserIdsRequest,
)
from app.modules.security.services import PermissionService

router = APIRouter(prefix="/security", tags=["security-permissions"])


@router.get("/me/permissions", response_model=MyPermissionsResponse)
def my_permissions(
    user: User = Depends(get_current_user),
    service: PermissionService = Depends(get_permission_service),
):
    return MyPermissionsResponse(
        permissions=sorted(service.permissions_for_user(user)),
        group_ids=service.group_ids_for_user(user.id),
    )


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission(CAN_VIEW_SECURITY))],
)
def list_permissions(
    service: PermissionService = Depends(get_permission_service),
):
    return service.list_permissions()


@router.get(
    "/groups",
    response_model=list[UserGroupResponse],
    dependencies=[Depends(require_permission(CAN_VIEW_SECURITY))],
)
def list_groups(
    service: PermissionService = Depends(get_permission_service),
):
    return service.list_groups()


@router.post(
    "/groups", response_model=UserGroupResponse, status_code=status.HTTP_201_CREATED
)
def create_group(
    request: UserGroupCreateRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.create_group(request, actor=user)


@router.patch("/groups/{group_id}", response_model=UserGroupResponse)
def update_group(
    group_id: UUID,
    request: UserGroupUpdateRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.update_group(group_id, request, actor=user)


@router.put("/groups/{group_id}", response_model=UserGroupResponse)
def save_group(
    group_id: UUID,
    request: UserGroupSaveRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.save_group(group_id, request, actor=user)


@router.put("/groups/{group_id}/permissions", response_model=UserGroupResponse)
def replace_group_permissions(
    group_id: UUID,
    request: PermissionCodesRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.replace_group_permissions(
        group_id, request.permission_codes, actor=user
    )


@router.put("/groups/{group_id}/users", response_model=UserGroupResponse)
def replace_group_users(
    group_id: UUID,
    request: UserIdsRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.replace_group_users(group_id, request.user_ids, actor=user)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: UUID,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    service.delete_group(group_id, actor=user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/groups/{group_id}/audit",
    response_model=list[AuditEventResponse],
    dependencies=[Depends(require_permission(CAN_VIEW_SECURITY))],
)
def security_group_audit_history(
    group_id: UUID,
    query: AuditHistoryQuery = Depends(),
    service: PermissionService = Depends(get_permission_service),
    audit: AuditReaderPort = Depends(get_audit_reader),
):
    service.get_group(group_id)
    return audit.get_logs_for_entity(
        EntityType.SECURITY_USER_GROUP.value,
        str(group_id),
        limit=query.limit,
        offset=query.offset,
    )


@router.get(
    "/users/{user_id}/groups",
    response_model=list[UUID],
    dependencies=[Depends(require_permission(CAN_VIEW_SECURITY))],
)
def user_groups(
    user_id: UUID,
    service: PermissionService = Depends(get_permission_service),
):
    return service.group_ids_for_user(user_id)


@router.put("/users/{user_id}/groups", response_model=list[UUID])
def replace_user_groups(
    user_id: UUID,
    request: GroupIdsRequest,
    user: User = Depends(require_permission(CAN_MANAGE_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    return service.replace_user_groups(user_id, request.group_ids, actor=user)

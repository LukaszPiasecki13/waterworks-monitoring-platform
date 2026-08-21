"""API for user security context — current user's permissions and groups."""

from fastapi import APIRouter, Depends

from app.modules.core_data.models import User
from app.modules.security.dependencies import (
    get_current_user,
    get_permission_service,
)
from app.modules.security.schemas.permissions import MyPermissionsResponse
from app.modules.security.services import PermissionService

router = APIRouter(prefix="/security", tags=["security-permissions"])


@router.get("/me/permissions", response_model=MyPermissionsResponse)
def my_permissions(
    user: User = Depends(get_current_user),
    service: PermissionService = Depends(get_permission_service),
):
    """Get current user's permissions and group IDs."""
    return MyPermissionsResponse(
        permissions=sorted(service.permissions_for_user(user)),
        group_ids=service.group_ids_for_user(user.id),
    )

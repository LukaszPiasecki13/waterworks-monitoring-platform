"""Platform security groups API endpoints (temporary location).

TODO: Move to app/modules/platform/api/groups.py when platform module is created.
"""

from fastapi import APIRouter, Depends

from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import (
    get_permission_service,
    require_platform_permission,
)
from app.modules.security.permission_catalog import PLATFORM_MANAGE_ORGANIZATIONS
from app.modules.security.services.permissions import PermissionService

router = APIRouter(prefix="/groups", tags=["platform-groups"])


@router.get("")
def list_platform_groups(
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_MANAGE_ORGANIZATIONS)
    ),
    service: PermissionService = Depends(get_permission_service),
):
    """List platform-level security groups."""
    return service.list_platform_groups()

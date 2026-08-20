"""Organization security groups API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.modules.security.access import OrganizationAccess
from app.modules.security.dependencies import (
    get_permission_service,
    require_org_access,
)
from app.modules.security.permission_catalog import CAN_VIEW_SECURITY
from app.modules.security.services.permissions import PermissionService

router = APIRouter(prefix="/orgs/{org_id}/groups", tags=["organization-groups"])


@router.get("")
def list_org_groups(
    org_id: UUID = Path(...),
    org_access: OrganizationAccess = Depends(require_org_access(CAN_VIEW_SECURITY)),
    service: PermissionService = Depends(get_permission_service),
):
    """List security groups for this organization."""
    return service.list_org_groups(org_id)

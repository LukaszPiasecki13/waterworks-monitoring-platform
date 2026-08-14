"""Organizations API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.core_data.dependencies import get_organization_service
from app.modules.core_data.models import User
from app.modules.core_data.schemas.organizations import (
    ListOrganizationsRequest,
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.modules.core_data.schemas.users import PaginatedResponse
from app.modules.core_data.services.organizations import OrganizationService
from app.modules.security.dependencies import (
    get_current_user,
    require_permission,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_ORGANIZATIONS,
    CAN_VIEW_ORGANIZATIONS,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=PaginatedResponse[OrganizationResponse])
def list_organizations(
    query: ListOrganizationsRequest = Depends(),
    service: OrganizationService = Depends(get_organization_service),
    user: User = Depends(get_current_user),
):
    """List organizations."""
    orgs, total = service.list_all(query, actor=user)
    return PaginatedResponse(
        items=orgs,
        total=total,
        skip=query.skip,
        limit=query.limit,
    )


@router.post("", response_model=OrganizationResponse)
def create_organization(
    request: OrganizationCreateRequest,
    service: OrganizationService = Depends(get_organization_service),
    user: User = Depends(require_permission(CAN_MANAGE_ORGANIZATIONS)),
):
    """Create organization."""
    return service.create(request, actor=user)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: UUID,
    service: OrganizationService = Depends(get_organization_service),
    user: User = Depends(require_permission(CAN_VIEW_ORGANIZATIONS)),
):
    """Get organization by ID."""
    return service.get_by_id(org_id, actor=user)


@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: UUID,
    request: OrganizationUpdateRequest,
    service: OrganizationService = Depends(get_organization_service),
    user: User = Depends(require_permission(CAN_MANAGE_ORGANIZATIONS)),
):
    """Update organization."""
    return service.update(org_id, request, actor=user)


@router.delete("/{org_id}")
def delete_organization(
    org_id: UUID,
    service: OrganizationService = Depends(get_organization_service),
    user: User = Depends(require_permission(CAN_MANAGE_ORGANIZATIONS)),
):
    """Delete organization."""
    service.delete(org_id, actor=user)
    return {"message": "Organization deleted successfully"}

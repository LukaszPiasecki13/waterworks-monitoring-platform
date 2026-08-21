"""Platform audit log API endpoints."""

from fastapi import APIRouter, Depends

from app.core.audit import AuditReaderPort
from app.modules.audit.dependencies import get_audit_reader
from app.modules.audit.schemas import AuditEventResponse, AuditHistoryQuery
from app.modules.security.access import PlatformContext
from app.modules.security.dependencies import require_platform_permission
from app.modules.security.permission_catalog import PLATFORM_VIEW_AUDIT

router = APIRouter(prefix="/audit", tags=["platform-audit"])


@router.get("", response_model=list[AuditEventResponse])
def platform_audit(
    query: AuditHistoryQuery = Depends(),
    context: PlatformContext = Depends(
        require_platform_permission(PLATFORM_VIEW_AUDIT)
    ),
    audit: AuditReaderPort = Depends(get_audit_reader),
):
    """List all audit events (platform-level, requires PLATFORM_VIEW_AUDIT)."""
    return audit.list_all(limit=query.limit, offset=query.offset)

from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.config import get_settings
from app.core.dependencies import get_db
from app.modules.audit.dependencies import get_audit_service
from app.modules.core_data.models import User
from app.modules.core_data.repositories.users import UserRepository
from app.modules.core_data.repositories.users_organizations import (
    UsersOrganizationsRepository,
)
from app.modules.security.access import (
    OrganizationAccess,
    PlatformContext,
    get_organization_context,
    get_platform_context,
)
from app.modules.security.permission_catalog import (
    CAN_MANAGE_SECURITY,
)
from app.modules.security.repositories import PermissionRepository
from app.modules.security.services.auth import AuthService
from app.modules.security.services.context import UserContextService
from app.modules.security.services.permissions import PermissionService
from app.modules.security.services.token import TokenService

bearer_scheme = HTTPBearer(auto_error=False)


def get_token_service() -> TokenService:
    settings = get_settings()
    return TokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_user_repo(session: Session = Depends(get_db)) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(session)


def get_permission_repo(
    session: Session = Depends(get_db),
) -> PermissionRepository:
    return PermissionRepository(session)


def get_permission_service(
    repo: PermissionRepository = Depends(get_permission_repo),
    users: UserRepository = Depends(get_user_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> PermissionService:
    return PermissionService(repo, users, audit)


def get_auth_service(
    repo: UserRepository = Depends(get_user_repo),
    token_service: TokenService = Depends(get_token_service),
    permissions: PermissionService = Depends(get_permission_service),
    audit: AuditPort = Depends(get_audit_service),
) -> AuthService:
    return AuthService(repo, token_service, permissions, audit)


def get_user_context_service(
    permissions: PermissionService = Depends(get_permission_service),
) -> UserContextService:
    """Build user context service.

    MembersService injected via lazy import to break circular dependency:
    core_data.dependencies imports from security.dependencies, so we cannot
    import get_members_service at module load time.
    """
    from app.modules.core_data.dependencies import get_members_service

    members_service = get_members_service()
    return UserContextService(members_service, permissions)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repo),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    """Get current authenticated user from Authorization header."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = token_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id)
    except ValueError, TypeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(permission_code: str) -> Callable[..., User]:
    """Require a permission inherited from any user security group."""

    def dependency(
        user: User = Depends(get_current_user),
        permissions: PermissionService = Depends(get_permission_service),
    ) -> User:
        if not permissions.has_permission(user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


def require_assigned_permission(
    user: User = Depends(get_current_user),
    permissions: PermissionService = Depends(get_permission_service),
) -> User:
    """Require any permission currently present in the SQL catalog."""
    if not permissions.permissions_for_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user


def get_users_organizations_repo(
    session: Session = Depends(get_db),
) -> UsersOrganizationsRepository:
    """Get users-organizations repository dependency."""
    return UsersOrganizationsRepository(session)


def require_org_membership(
    org_id: UUID,
    user: User = Depends(get_current_user),
    members: UsersOrganizationsRepository = Depends(get_users_organizations_repo),
    permissions: PermissionService = Depends(get_permission_service),
) -> OrganizationAccess:
    """Build organization context from user and org_id.

    Raises:
        NotFoundError: If user is not a member of the organization.
    """
    return get_organization_context(org_id, user, members, permissions)


def require_org_access(*permission_codes: str):
    """Require org membership and at least one of the given permissions.

    Combines the membership check (404) with the permission check (403) in
    a single pass, returning the resulting access context for the service to use
    directly instead of re-deriving it.
    """

    def dependency(
        org_access: OrganizationAccess = Depends(require_org_membership),
    ) -> OrganizationAccess:
        if not org_access.permissions.intersection(permission_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return org_access

    return dependency


def require_platform_permission(*permission_codes: str):
    """Require platform-level (global) permissions.

    Returns PlatformContext instead of bare User — encapsulates platform permissions
    along with the actor, mirroring OrganizationAccess for org-scoped operations.
    Only checks platform groups (organization_id IS NULL).
    """

    def dependency(
        user: User = Depends(get_current_user),
        permissions: PermissionService = Depends(get_permission_service),
    ) -> PlatformContext:
        context = get_platform_context(user, permissions)
        if not context.permissions.intersection(permission_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return context

    return dependency


# Backward-compatible aliases for code that has not yet moved to an
# action-specific permission. They are group-based and never inspect User.status.
require_admin = require_permission(CAN_MANAGE_SECURITY)
require_staff = require_assigned_permission

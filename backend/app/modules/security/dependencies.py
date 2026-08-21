from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import NotFoundError
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
from app.modules.security.repositories import GroupRepository, PermissionRepository
from app.modules.security.services.auth import AuthService
from app.modules.security.services.groups import GroupService
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
        device_token_expire_hours=settings.device_token_expire_hours,
    )


def get_user_repo(session: Session = Depends(get_db)) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(session)


def get_permission_repo(
    session: Session = Depends(get_db),
) -> PermissionRepository:
    return PermissionRepository(session)


def get_group_repo(
    session: Session = Depends(get_db),
) -> GroupRepository:
    return GroupRepository(session)


def get_permission_service(
    repo: PermissionRepository = Depends(get_permission_repo),
    users: UserRepository = Depends(get_user_repo),
    group_repo: GroupRepository = Depends(get_group_repo),
) -> PermissionService:
    return PermissionService(repo, users, group_repo)


def get_group_service(
    repo: GroupRepository = Depends(get_group_repo),
    users: UserRepository = Depends(get_user_repo),
    permissions: PermissionService = Depends(get_permission_service),
    audit: AuditPort = Depends(get_audit_service),
) -> GroupService:
    return GroupService(repo, users, permissions, audit)


def get_auth_service(
    repo: UserRepository = Depends(get_user_repo),
    token_service: TokenService = Depends(get_token_service),
    permissions: PermissionService = Depends(get_permission_service),
    audit: AuditPort = Depends(get_audit_service),
) -> AuthService:
    return AuthService(repo, token_service, permissions, audit)


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


def get_users_organizations_repo(
    session: Session = Depends(get_db),
) -> UsersOrganizationsRepository:
    """Get users-organizations repository dependency."""
    return UsersOrganizationsRepository(session)


def _require_any_permission(permissions: set[str], required: tuple[str, ...]) -> None:
    """Raise 403 unless `permissions` contains at least one of `required`."""
    if not permissions.intersection(required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


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
        _require_any_permission(org_access.permissions, permission_codes)
        return org_access

    return dependency


def require_org_or_platform_permission(*platform_permission_codes: str):
    """Require org membership, or one of the given platform-level permissions.

    Lets platform admins operate on org-scoped resources (e.g. memberships)
    without being a member of the organization themselves.
    """

    def dependency(
        org_id: UUID,
        user: User = Depends(get_current_user),
        members: UsersOrganizationsRepository = Depends(get_users_organizations_repo),
        permissions: PermissionService = Depends(get_permission_service),
    ) -> OrganizationAccess:
        try:
            return get_organization_context(org_id, user, members, permissions)
        except NotFoundError:
            pass

        platform_context = get_platform_context(user, permissions)
        _require_any_permission(platform_context.permissions, platform_permission_codes)
        return OrganizationAccess(actor=user, organization_id=org_id, permissions=set())

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
        _require_any_permission(context.permissions, permission_codes)
        return context

    return dependency

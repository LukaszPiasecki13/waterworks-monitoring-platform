"""Access control context for organization-scoped and platform-level operations."""

from dataclasses import dataclass
from uuid import UUID

from app.core.errors import NotFoundError
from app.modules.core_data.models import User


@dataclass(frozen=True)
class PlatformContext:
    """Context for platform-level (global) administrative operations.

    Encapsulates:
    - The actor (super admin user)
    - Permissions at platform level only (from groups with organization_id IS NULL)
    """

    actor: User
    permissions: set[str]


@dataclass(frozen=True)
class OrganizationAccess:
    """Context for accessing organization-scoped resources.

    Encapsulates:
    - The actor (user) requesting access
    - The organization scope
    - Permissions in that organization (for audit/logging)

    Replaces duplicated 404-vs-403 logic across service methods.
    """

    actor: User
    organization_id: UUID
    permissions: set[str]


def get_organization_context(
    org_id: UUID,
    user: User,
    members_repo,
    permissions_service,
) -> OrganizationAccess:
    """Validate user membership in organization and return context.

    Raises:
        NotFoundError: If user is not a member of the organization.

    This replaces the pattern of checking membership in every service method.
    The dependency layer ensures membership + permissions before passing to service.
    """
    if not members_repo.is_member(user.id, org_id):
        raise NotFoundError

    perms = permissions_service.permissions_for_user_in_org(user, org_id)

    return OrganizationAccess(
        actor=user,
        organization_id=org_id,
        permissions=perms,
    )


def get_platform_context(user: User, permissions_service) -> PlatformContext:
    """Build platform-level access context.

    Platform context includes only permissions from groups with organization_id IS NULL.
    """
    perms = permissions_service.permissions_for_user_at_platform_level(user)
    return PlatformContext(actor=user, permissions=perms)

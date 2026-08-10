"""Organization scope helpers — enforce isolation between tenants."""

from uuid import UUID

from app.core.errors import NotFoundError
from app.modules.core_data.models import User


def resolve_organization_id(actor: User, requested_organization_id: UUID) -> UUID:
    """Non-platform admin is pinned to own organization."""
    if actor.organization_id is not None:
        return actor.organization_id
    return requested_organization_id


def assert_same_organization(actor: User, resource_organization_id: UUID) -> None:
    """Deny access to cross-org resource (raise NotFoundError to hide existence)."""
    if actor.organization_id is not None and actor.organization_id != resource_organization_id:
        raise NotFoundError("Resource not found")

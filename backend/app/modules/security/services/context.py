"""User context service — environments and permissions."""

from app.modules.core_data.models import User
from app.modules.core_data.services.members import MembersService
from app.modules.security.schemas.context import (
    OrganizationEnvironment,
    PlatformEnvironment,
    UserContextResponse,
)
from app.modules.security.services.permissions import PermissionService


class UserContextService:
    """Build user's access context: organizations + permissions."""

    def __init__(
        self,
        members_service: MembersService,
        permissions_service: PermissionService,
    ):
        self.members_service = members_service
        self.permissions_service = permissions_service

    def get_context(self, user: User) -> UserContextResponse:
        """Build complete context: organizations + permissions."""
        organizations = []
        orgs = self.members_service.get_organizations_for_user(user.id)

        for org in orgs:
            perms = self.permissions_service.permissions_for_user_in_org(user, org.id)
            organizations.append(
                OrganizationEnvironment(
                    organization_id=org.id,
                    organization_name=org.name,
                    permissions=sorted(perms),
                )
            )

        platform_perms = (
            self.permissions_service.permissions_for_user_at_platform_level(user)
        )
        platform = (
            PlatformEnvironment(permissions=sorted(platform_perms))
            if platform_perms
            else None
        )

        return UserContextResponse(organizations=organizations, platform=platform)

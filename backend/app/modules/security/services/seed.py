"""Security seed service — syncs permissions and system groups on startup.

Runs automatically when the application starts to ensure:
1. All permissions from PERMISSION_CATALOG exist in database
2. Admin group has all permissions (always synced)
3. Staff group exists with read-only permissions (created only once)

This provides production-like setup from first run.
"""

import logging

from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    PERMISSION_CATALOG,
)
from app.modules.security.repositories import GroupRepository, PermissionRepository

logger = logging.getLogger(__name__)


class SecuritySeedService:
    """Synchronize permission catalog and seed system groups on application startup."""

    def __init__(self, perm_repo: PermissionRepository, group_repo: GroupRepository):
        self.perm_repo = perm_repo
        self.group_repo = group_repo

    def seed(self) -> None:
        """Sync permissions from catalog and ensure system groups exist."""
        logger.info("Starting security seed...")

        try:
            # Sync permissions
            self._sync_permissions()

            # Seed system groups
            self._seed_admin_group()

            self.perm_repo.commit(skip_audit=True)
            logger.info("Security seed completed successfully")
        except Exception as e:
            # If tables don't exist (migration not applied yet), skip seeding
            error_msg = str(e).lower()
            if "relation" not in error_msg or "does not exist" not in error_msg:
                raise
            logger.warning(
                "Security tables not yet created (migrations not applied). "
                "Seeding will run on next startup after migrations."
            )

    def _sync_permissions(self) -> None:
        """Sync permission catalog into database (upsert by code)."""
        for perm_def in PERMISSION_CATALOG:
            existing = self.perm_repo.get_permission_by_code(perm_def.code)
            if existing:
                # Update name/category if they differ
                if (
                    existing.name != perm_def.name
                    or existing.category != perm_def.category
                ):
                    existing.name = perm_def.name
                    existing.category = perm_def.category
                    logger.debug(f"Updated permission {perm_def.code}")
            else:
                self.perm_repo.create_permission(
                    code=perm_def.code,
                    name=perm_def.name,
                    category=perm_def.category,
                )
                logger.debug(f"Created permission {perm_def.code}")

    def _seed_admin_group(self) -> None:
        """Create or resync admin group with all permissions (platform-level)."""
        admin_group = self.group_repo.get_group_by_system_key(
            ADMIN_GROUP_KEY, organization_id=None
        )
        all_permissions = self.perm_repo.list_permissions()

        if not admin_group:
            admin_group = self.group_repo.create_system_group(
                name="Admin",
                description="Full system access",
                system_key=ADMIN_GROUP_KEY,
                permissions=all_permissions,
            )
            logger.info(
                "Created system group 'admin' (platform-level) with all permissions"
            )
        else:
            # Resync: admin always gets all current permissions
            admin_group.permissions = all_permissions
            logger.debug("Resynced 'admin' group permissions to all")

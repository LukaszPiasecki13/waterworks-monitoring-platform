"""Security seed service — syncs permissions and system groups on startup."""

import logging

from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    PERMISSION_CATALOG,
    STAFF_GROUP_KEY,
    VIEW_PERMISSIONS,
)
from app.modules.security.repositories import PermissionRepository

logger = logging.getLogger(__name__)


class SecuritySeedService:
    """Synchronize permission catalog and seed system groups on application startup."""

    def __init__(self, repo: PermissionRepository):
        self.repo = repo

    def seed(self) -> None:
        """Sync permissions from catalog and ensure system groups exist."""
        logger.info("Starting security seed...")

        # Sync permissions
        self._sync_permissions()

        # Seed system groups
        self._seed_admin_group()
        self._seed_staff_group()

        self.repo.commit(skip_audit=True)
        logger.info("Security seed completed successfully")

    def _sync_permissions(self) -> None:
        """Sync permission catalog into database (upsert by code)."""
        for perm_def in PERMISSION_CATALOG:
            existing = self.repo.get_permission_by_code(perm_def.code)
            if existing:
                # Update name/category if they differ
                if existing.name != perm_def.name or existing.category != perm_def.category:
                    existing.name = perm_def.name
                    existing.category = perm_def.category
                    logger.debug(f"Updated permission {perm_def.code}")
            else:
                self.repo.create_permission(
                    code=perm_def.code,
                    name=perm_def.name,
                    category=perm_def.category,
                )
                logger.debug(f"Created permission {perm_def.code}")

    def _seed_admin_group(self) -> None:
        """Create or resync admin group with all permissions."""
        admin_group = self.repo.get_group_by_system_key(ADMIN_GROUP_KEY)
        all_permissions = self.repo.list_permissions()

        if not admin_group:
            admin_group = self.repo.create_system_group(
                name="Admin",
                description="Full system access",
                system_key=ADMIN_GROUP_KEY,
                permissions=all_permissions,
            )
            logger.info("Created system group 'admin' with all permissions")
        else:
            # Resync: admin always gets all current permissions
            admin_group.permissions = all_permissions
            logger.debug("Resynced 'admin' group permissions to all")

    def _seed_staff_group(self) -> None:
        """Create staff group (only at first creation) with VIEW permissions."""
        staff_group = self.repo.get_group_by_system_key(STAFF_GROUP_KEY)

        if not staff_group:
            view_permissions = [
                perm
                for perm in self.repo.list_permissions()
                if perm.code in VIEW_PERMISSIONS
            ]
            staff_group = self.repo.create_system_group(
                name="Staff",
                description="Read-only access",
                system_key=STAFF_GROUP_KEY,
                permissions=view_permissions,
            )
            logger.info("Created system group 'staff' with CAN_VIEW_* permissions")
        else:
            # Staff group exists - do not modify its permissions (editable by admin)
            logger.debug("Staff group already exists, permissions left unchanged")

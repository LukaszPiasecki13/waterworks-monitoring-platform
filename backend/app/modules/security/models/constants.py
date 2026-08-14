"""Deprecated: Permission constants have been moved to
app.modules.security.permission_catalog.
"""

# Re-export for backwards compatibility
from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    CAN_MANAGE_ASSETS,
    CAN_MANAGE_ATTACHMENTS,
    CAN_MANAGE_ORGANIZATIONS,
    CAN_MANAGE_SECURITY,
    CAN_MANAGE_USERS,
    CAN_VIEW_ASSETS,
    CAN_VIEW_ATTACHMENTS,
    CAN_VIEW_ORGANIZATIONS,
    CAN_VIEW_SECURITY,
    CAN_VIEW_USERS,
    STAFF_GROUP_KEY,
)

__all__ = [
    "ADMIN_GROUP_KEY",
    "CAN_MANAGE_ASSETS",
    "CAN_MANAGE_ATTACHMENTS",
    "CAN_MANAGE_ORGANIZATIONS",
    "CAN_MANAGE_SECURITY",
    "CAN_MANAGE_USERS",
    "CAN_VIEW_ASSETS",
    "CAN_VIEW_ATTACHMENTS",
    "CAN_VIEW_ORGANIZATIONS",
    "CAN_VIEW_SECURITY",
    "CAN_VIEW_USERS",
    "STAFF_GROUP_KEY",
]

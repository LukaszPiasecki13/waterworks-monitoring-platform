"""Statyczny katalog uprawnień synchronizowany z bazą przy starcie aplikacji."""

from dataclasses import dataclass
from typing import Literal

# Organization-scoped permission codes
CAN_VIEW_USERS = "CAN_VIEW_USERS"
CAN_MANAGE_USERS = "CAN_MANAGE_USERS"
CAN_VIEW_SECURITY = "CAN_VIEW_SECURITY"
CAN_MANAGE_SECURITY = "CAN_MANAGE_SECURITY"
CAN_VIEW_ATTACHMENTS = "CAN_VIEW_ATTACHMENTS"
CAN_MANAGE_ATTACHMENTS = "CAN_MANAGE_ATTACHMENTS"
CAN_VIEW_ORGANIZATIONS = "CAN_VIEW_ORGANIZATIONS"
CAN_MANAGE_ORGANIZATIONS = "CAN_MANAGE_ORGANIZATIONS"
CAN_VIEW_ASSETS = "CAN_VIEW_ASSETS"
CAN_MANAGE_ASSETS = "CAN_MANAGE_ASSETS"

# Platform-level permission codes
PLATFORM_VIEW_ORGANIZATIONS = "PLATFORM_VIEW_ORGANIZATIONS"
PLATFORM_MANAGE_ORGANIZATIONS = "PLATFORM_MANAGE_ORGANIZATIONS"
PLATFORM_VIEW_USERS = "PLATFORM_VIEW_USERS"
PLATFORM_MANAGE_USERS = "PLATFORM_MANAGE_USERS"
PLATFORM_MANAGE_MEMBERSHIPS = "PLATFORM_MANAGE_MEMBERSHIPS"
PLATFORM_VIEW_AUDIT = "PLATFORM_VIEW_AUDIT"
PLATFORM_MANAGE_DEVICE_PROVISIONING = "PLATFORM_MANAGE_DEVICE_PROVISIONING"

# System group keys
ADMIN_GROUP_KEY = "admin"
STAFF_GROUP_KEY = "staff"

# Organization-scoped system group keys (per-organization, paired with organization_id)
ORG_ADMIN_GROUP_KEY = "org_admin"
ORG_OPERATOR_GROUP_KEY = "org_operator"
ORG_VIEWER_GROUP_KEY = "org_viewer"


@dataclass(frozen=True)
class PermissionDefinition:
    """Definicja uprawnienia w katalagu."""

    code: str
    name: str
    category: str
    plane: Literal["organization", "platform"] = "organization"


PERMISSION_CATALOG = [
    # Organization-scoped permissions (operate on org's members, assets, groups)
    PermissionDefinition(
        code=CAN_VIEW_USERS,
        name="Podgląd członków organizacji",
        category="Użytkownicy",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_USERS,
        name="Zarządzanie członkami organizacji",
        category="Użytkownicy",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_VIEW_SECURITY,
        name="Podgląd grup bezpieczeństwa organizacji",
        category="Bezpieczeństwo",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_SECURITY,
        name="Zarządzanie grupami bezpieczeństwa organizacji",
        category="Bezpieczeństwo",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ATTACHMENTS,
        name="Podgląd załączników organizacji",
        category="Załączniki",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ATTACHMENTS,
        name="Zarządzanie załącznikami organizacji",
        category="Załączniki",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ORGANIZATIONS,
        name="Podgląd własnej organizacji",
        category="Rejestr obiektów",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ORGANIZATIONS,
        name="Zarządzanie własną organizacją",
        category="Rejestr obiektów",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ASSETS,
        name="Podgląd obiektów, urządzeń i punktów pomiarowych",
        category="Rejestr obiektów",
        plane="organization",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ASSETS,
        name="Zarządzanie obiektami, urządzeniami i punktami pomiarowymi",
        category="Rejestr obiektów",
        plane="organization",
    ),
    # Platform-level permissions (operate on global registry)
    PermissionDefinition(
        code=PLATFORM_VIEW_ORGANIZATIONS,
        name="Podgląd rejestru organizacji",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_MANAGE_ORGANIZATIONS,
        name="Zarządzanie organizacjami",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_VIEW_USERS,
        name="Podgląd globalnego rejestru kont",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_MANAGE_USERS,
        name="Zarządzanie kontami",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_MANAGE_MEMBERSHIPS,
        name="Zarządzanie członkostwami",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_VIEW_AUDIT,
        name="Podgląd audytu globalnego",
        category="Platforma",
        plane="platform",
    ),
    PermissionDefinition(
        code=PLATFORM_MANAGE_DEVICE_PROVISIONING,
        name="Zarządzanie provisioningiem urządzeń",
        category="Platforma",
        plane="platform",
    ),
]

# Organization-scoped permissions (all org-plane permission codes)
ORG_PLANE_PERMISSION_CODES = {
    CAN_VIEW_USERS,
    CAN_MANAGE_USERS,
    CAN_VIEW_SECURITY,
    CAN_MANAGE_SECURITY,
    CAN_VIEW_ATTACHMENTS,
    CAN_MANAGE_ATTACHMENTS,
    CAN_VIEW_ORGANIZATIONS,
    CAN_MANAGE_ORGANIZATIONS,
    CAN_VIEW_ASSETS,
    CAN_MANAGE_ASSETS,
}

# Organization-scoped view permissions only
VIEW_PERMISSIONS = {
    CAN_VIEW_USERS,
    CAN_VIEW_SECURITY,
    CAN_VIEW_ATTACHMENTS,
    CAN_VIEW_ORGANIZATIONS,
    CAN_VIEW_ASSETS,
}

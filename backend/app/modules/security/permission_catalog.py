"""Statyczny katalog uprawnień synchronizowany z bazą przy starcie aplikacji."""

from dataclasses import dataclass

# Permission codes
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

# System group keys
ADMIN_GROUP_KEY = "admin"
STAFF_GROUP_KEY = "staff"


@dataclass(frozen=True)
class PermissionDefinition:
    """Definicja uprawnienia w katalagu."""

    code: str
    name: str
    category: str


PERMISSION_CATALOG = [
    PermissionDefinition(
        code=CAN_VIEW_USERS,
        name="Podgląd użytkowników",
        category="Użytkownicy",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_USERS,
        name="Zarządzanie użytkownikami",
        category="Użytkownicy",
    ),
    PermissionDefinition(
        code=CAN_VIEW_SECURITY,
        name="Podgląd bezpieczeństwa",
        category="Bezpieczeństwo",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_SECURITY,
        name="Zarządzanie bezpieczeństwem",
        category="Bezpieczeństwo",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ATTACHMENTS,
        name="Podgląd załączników",
        category="Załączniki",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ATTACHMENTS,
        name="Zarządzanie załącznikami",
        category="Załączniki",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ORGANIZATIONS,
        name="Podgląd organizacji",
        category="Rejestr obiektów",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ORGANIZATIONS,
        name="Zarządzanie organizacjami",
        category="Rejestr obiektów",
    ),
    PermissionDefinition(
        code=CAN_VIEW_ASSETS,
        name="Podgląd obiektów, urządzeń i punktów pomiarowych",
        category="Rejestr obiektów",
    ),
    PermissionDefinition(
        code=CAN_MANAGE_ASSETS,
        name="Zarządzanie obiektami, urządzeniami i punktami pomiarowymi",
        category="Rejestr obiektów",
    ),
]

VIEW_PERMISSIONS = {
    CAN_VIEW_USERS,
    CAN_VIEW_SECURITY,
    CAN_VIEW_ATTACHMENTS,
    CAN_VIEW_ORGANIZATIONS,
    CAN_VIEW_ASSETS,
}

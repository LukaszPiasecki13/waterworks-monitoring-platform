"""Unit tests for PermissionService."""

from sqlalchemy.orm import Session

from app.modules.core_data.models import User
from app.modules.core_data.repositories import UserRepository
from app.modules.security.models import Permission
from app.modules.security.repositories.permissions import PermissionRepository
from app.modules.security.services.permissions import PermissionService


def _permission_service(session: Session) -> PermissionService:
    return PermissionService(
        PermissionRepository(session), UserRepository(session), None
    )


def _user(session: Session, username: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.org",
        hashed_password="unused",
    )
    session.add(user)
    session.flush()
    return user


def _permission(session: Session, code: str, name: str, category: str) -> Permission:
    """Permission codes are reference data (see permission_catalog.py) that may
    already exist in the target database, so reuse rather than duplicate."""
    existing = PermissionRepository(session).get_permission_by_code(code)
    if existing:
        return existing
    permission = Permission(code=code, name=name, category=category)
    session.add(permission)
    session.flush()
    return permission


def test_list_permissions_returns_all_permissions(db_session: Session) -> None:
    """list_permissions() returns all registered permissions."""
    _permission(db_session, "CAN_VIEW_USERS", "View", "Users")
    _permission(db_session, "CAN_MANAGE_USERS", "Manage", "Users")
    db_session.commit()

    service = _permission_service(db_session)
    permissions = service.list_permissions()

    codes = {p.code for p in permissions}
    assert "CAN_VIEW_USERS" in codes
    assert "CAN_MANAGE_USERS" in codes

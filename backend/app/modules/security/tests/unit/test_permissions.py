from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.modules.core_data.models import User
from app.modules.core_data.repositories import UserRepository
from app.modules.security.models import Permission, UserGroup
from app.modules.security.repositories import PermissionRepository
from app.modules.security.schemas.permissions import (
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
)
from app.modules.security.services.permissions import PermissionService


def _service(session: Session) -> PermissionService:
    return PermissionService(
        PermissionRepository(session), UserRepository(session), MagicMock()
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


def _system_group(
    session: Session,
    system_key: str,
    name: str,
    permissions: list[Permission] | None = None,
) -> UserGroup:
    """System groups (system_key) are singletons synced by SecuritySeedService,
    so reuse the existing row rather than inserting a duplicate."""
    existing = PermissionRepository(session).get_group_by_system_key(system_key)
    if existing:
        return existing
    group = UserGroup(
        name=name,
        description="Protected",
        is_system=True,
        system_key=system_key,
        permissions=permissions or [],
    )
    session.add(group)
    session.flush()
    return group


def test_user_inherits_union_of_permissions_from_multiple_groups(
    db_session: Session,
) -> None:
    view = _permission(db_session, "CAN_VIEW_USERS", "View", "Users")
    manage = _permission(db_session, "CAN_MANAGE_USERS", "Manage", "Users")
    first = UserGroup(name="Data provider", permissions=[view])
    second = UserGroup(name="Reviewer", permissions=[manage])
    user = _user(db_session, "ala")
    db_session.add_all([first, second])
    db_session.flush()

    service = _service(db_session)
    service.replace_user_groups(user.id, [first.id, second.id], actor=user)

    assert service.permissions_for_user(user) == {
        "CAN_VIEW_USERS",
        "CAN_MANAGE_USERS",
    }


def test_system_group_definition_cannot_be_modified(db_session: Session) -> None:
    group = _system_group(db_session, "admin", "Admin")
    db_session.commit()

    with pytest.raises(BadRequestError) as error:
        _service(db_session).update_group(
            group.id,
            UserGroupUpdateRequest(name="Changed"),
            actor=group,
        )

    assert error.value.status_code == 400


def test_system_group_permission_matrix_cannot_be_modified(
    db_session: Session,
) -> None:
    group = _system_group(db_session, "admin", "Admin")
    db_session.commit()

    with pytest.raises(BadRequestError) as error:
        _service(db_session).replace_group_permissions(group.id, [], actor=group)

    assert error.value.status_code == 400


def test_staff_group_permissions_are_editable_but_metadata_stays_locked(
    db_session: Session,
) -> None:
    """Admins can tune STAFF permissions; name/description stay locked."""
    _permission(db_session, "CAN_VIEW_USERS", "View", "Users")
    _permission(db_session, "CAN_MANAGE_USERS", "Manage", "Users")
    group = _system_group(db_session, "staff", "Staff")
    actor = _user(db_session, "staff-admin")
    db_session.commit()

    service = _service(db_session)
    updated = service.replace_group_permissions(
        group.id, ["CAN_VIEW_USERS"], actor=actor
    )
    assert [permission.code for permission in updated["permissions"]] == [
        "CAN_VIEW_USERS"
    ]

    saved = service.save_group(
        group.id,
        UserGroupSaveRequest(
            name="Staff",
            description="Read-only access",
            permission_codes=["CAN_VIEW_USERS", "CAN_MANAGE_USERS"],
            user_ids=[],
        ),
        actor=actor,
    )
    assert {permission.code for permission in saved["permissions"]} == {
        "CAN_VIEW_USERS",
        "CAN_MANAGE_USERS",
    }

    with pytest.raises(BadRequestError) as error:
        service.save_group(
            group.id,
            UserGroupSaveRequest(
                name="Inna nazwa",
                description="Protected",
                permission_codes=["CAN_VIEW_USERS", "CAN_MANAGE_USERS"],
                user_ids=[],
            ),
            actor=actor,
        )
    assert error.value.status_code == 400


def test_permission_only_group_change_is_persisted(db_session: Session) -> None:
    """Permission codes are included in the group snapshot."""
    view = _permission(db_session, "CAN_VIEW_USERS", "View", "Users")
    _permission(db_session, "CAN_MANAGE_USERS", "Manage", "Users")
    group = UserGroup(name="Zespol", permissions=[view])
    actor = _user(db_session, "aktor")
    db_session.add(group)
    db_session.commit()

    service = _service(db_session)
    service.replace_group_permissions(
        group.id, ["CAN_VIEW_USERS", "CAN_MANAGE_USERS"], actor=actor
    )

    stored = db_session.get(UserGroup, group.id)
    assert {permission.code for permission in stored.permissions} == {
        "CAN_VIEW_USERS",
        "CAN_MANAGE_USERS",
    }

"""Unit tests for GroupService."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError, ConflictError
from app.modules.core_data.models import Organization, User
from app.modules.core_data.repositories import UserRepository
from app.modules.security.models import Permission, UserGroup
from app.modules.security.repositories.groups import GroupRepository
from app.modules.security.repositories.permissions import PermissionRepository
from app.modules.security.schemas.groups import (
    UserGroupCreateRequest,
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
)
from app.modules.security.services.groups import GroupService
from app.modules.security.services.permissions import PermissionService


def _group_service(session: Session) -> GroupService:
    perm_repo = PermissionRepository(session)
    user_repo = UserRepository(session)
    perm_service = PermissionService(perm_repo, user_repo)
    return GroupService(
        GroupRepository(session),
        user_repo,
        perm_service,
        MagicMock(),
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
    existing = GroupRepository(session).get_group_by_system_key(system_key)
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

    service = _group_service(db_session)
    service.replace_user_groups(user.id, [first.id, second.id], actor=user)

    perm_repo = PermissionRepository(db_session)
    user_repo = UserRepository(db_session)
    perm_service = PermissionService(perm_repo, user_repo)
    assert perm_service.permissions_for_user(user) == {
        "CAN_VIEW_USERS",
        "CAN_MANAGE_USERS",
    }


def test_system_group_definition_cannot_be_modified(db_session: Session) -> None:
    group = _system_group(db_session, "admin", "Admin")
    db_session.commit()

    with pytest.raises(BadRequestError) as error:
        _group_service(db_session).update_group(
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
        _group_service(db_session).replace_group_permissions(group.id, [], actor=group)

    assert error.value.status_code == 400


def test_staff_group_permissions_are_editable_but_metadata_stays_locked(
    db_session: Session,
) -> None:
    """Admins can tune STAFF permissions; name/description stay locked."""
    _permission(db_session, "PLATFORM_VIEW_USERS", "View", "Users")
    _permission(db_session, "PLATFORM_MANAGE_USERS", "Manage", "Users")
    group = _system_group(db_session, "staff", "Staff")
    actor = _user(db_session, "staff-admin")
    db_session.commit()

    service = _group_service(db_session)
    updated = service.replace_group_permissions(
        group.id, ["PLATFORM_VIEW_USERS"], actor=actor
    )
    assert [permission.code for permission in updated["permissions"]] == [
        "PLATFORM_VIEW_USERS"
    ]

    saved = service.save_group(
        group.id,
        UserGroupSaveRequest(
            name="Staff",
            description="Read-only access",
            permission_codes=["PLATFORM_VIEW_USERS", "PLATFORM_MANAGE_USERS"],
            user_ids=[],
        ),
        actor=actor,
    )
    assert {permission.code for permission in saved["permissions"]} == {
        "PLATFORM_VIEW_USERS",
        "PLATFORM_MANAGE_USERS",
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
    view = _permission(db_session, "PLATFORM_VIEW_USERS", "View", "Users")
    _permission(db_session, "PLATFORM_MANAGE_USERS", "Manage", "Users")
    group = UserGroup(name="Zespol", permissions=[view])
    actor = _user(db_session, "aktor")
    db_session.add(group)
    db_session.commit()

    service = _group_service(db_session)
    service.replace_group_permissions(
        group.id, ["PLATFORM_VIEW_USERS", "PLATFORM_MANAGE_USERS"], actor=actor
    )

    stored = db_session.get(UserGroup, group.id)
    assert {permission.code for permission in stored.permissions} == {
        "PLATFORM_VIEW_USERS",
        "PLATFORM_MANAGE_USERS",
    }


def test_create_group_is_scoped_to_organization_not_global(
    db_session: Session,
) -> None:
    """Regression test for the cross-org name collision bug (03-plan-overview.md
    risk 7.1b): two different organizations must both be able to have a group
    named "Operator" without a false ConflictError."""
    org_a = Organization(name="Org A")
    org_b = Organization(name="Org B")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    actor = _user(db_session, "org-admin")
    db_session.commit()

    service = _group_service(db_session)
    service.create_group(
        UserGroupCreateRequest(name="Operator", description="", permission_codes=[]),
        actor=actor,
        organization_id=org_a.id,
    )

    # Same name in a different organization must succeed, not raise ConflictError.
    created_in_b = service.create_group(
        UserGroupCreateRequest(name="Operator", description="", permission_codes=[]),
        actor=actor,
        organization_id=org_b.id,
    )

    assert created_in_b["name"] == "Operator"

    groups_in_b = service.list_org_groups(org_b.id)
    assert len(groups_in_b) == 1
    assert groups_in_b[0]["id"] == created_in_b["id"]

    groups_in_a = service.list_org_groups(org_a.id)
    assert len(groups_in_a) == 1
    assert groups_in_a[0]["id"] != created_in_b["id"]


def test_create_group_without_organization_id_stays_platform_scoped(
    db_session: Session,
) -> None:
    """Backward compatibility with the legacy /security/groups endpoint
    (security/api/permissions.py), which calls create_group without
    organization_id."""
    actor = _user(db_session, "platform-admin")
    db_session.commit()

    service = _group_service(db_session)
    created = service.create_group(
        UserGroupCreateRequest(
            name="Platform Only", description="", permission_codes=[]
        ),
        actor=actor,
    )

    platform_groups = service.list_platform_groups()
    assert any(g["id"] == created["id"] for g in platform_groups)


def test_validate_group_name_detects_duplicate_in_same_org(db_session: Session) -> None:
    """_validate_group_name() raises ConflictError when duplicate name exists
    in the same organization."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    # Create first group
    group1 = UserGroup(name="Operators", organization_id=org.id)
    db_session.add(group1)
    db_session.flush()

    service = _group_service(db_session)
    # Should raise ConflictError when attempting to validate duplicate name
    # in the same organization (used in create_group path)
    with pytest.raises(ConflictError):
        service._validate_group_name("Operators", group_id=None, organization_id=org.id)


def test_validate_group_name_allows_same_name_in_different_org(
    db_session: Session,
) -> None:
    """_validate_group_name() allows identical names in different organizations
    (regression test for bug 7.1b)."""
    org_a = Organization(name="Org A")
    org_b = Organization(name="Org B")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Create group in org A
    group_a = UserGroup(name="Operators", organization_id=org_a.id)
    db_session.add(group_a)
    db_session.flush()

    service = _group_service(db_session)
    # Same name in org B should NOT raise ConflictError
    service._validate_group_name("Operators", group_id=None, organization_id=org_b.id)
    # If we got here without exception, test passes


def test_validate_group_name_allows_unchanged_name_on_update(
    db_session: Session,
) -> None:
    """_validate_group_name() excludes the current group (by group_id) from
    duplicate check, allowing updates that don't change the name."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    group = UserGroup(name="Operators", organization_id=org.id)
    db_session.add(group)
    db_session.flush()

    service = _group_service(db_session)
    # Same name, but excluding this group from the check (group_id is provided)
    # should not raise ConflictError
    service._validate_group_name("Operators", group_id=group.id, organization_id=org.id)


def test_validate_group_name_allows_same_name_across_planes(
    db_session: Session,
) -> None:
    """_validate_group_name() allows identical names when one is on platform
    plane (organization_id=None) and one is org-scoped."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    # Create platform-scoped group
    platform_group = UserGroup(name="Operators", organization_id=None)
    db_session.add(platform_group)
    db_session.flush()

    service = _group_service(db_session)
    # Same name on org plane should not raise ConflictError
    service._validate_group_name("Operators", group_id=None, organization_id=org.id)


def test_list_groups_for_organization_returns_only_platform_groups_when_org_id_none(
    db_session: Session,
) -> None:
    """list_groups_for_organization(None) returns only platform-scoped groups."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    # Create mixed groups
    platform_group = UserGroup(name="Platform Group", organization_id=None)
    org_group = UserGroup(name="Org Group", organization_id=org.id)
    db_session.add_all([platform_group, org_group])
    db_session.flush()

    repo = GroupRepository(db_session)
    result = repo.list_groups_for_organization(None)

    # Should only contain platform groups
    assert any(g.name == "Platform Group" for g in result)
    assert not any(g.name == "Org Group" for g in result)


def test_list_groups_for_organization_returns_only_specified_org_groups(
    db_session: Session,
) -> None:
    """list_groups_for_organization(org_id) returns only groups belonging
    to that organization."""
    org_a = Organization(name="Org A")
    org_b = Organization(name="Org B")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    # Create mixed groups
    platform_group = UserGroup(name="Platform Group", organization_id=None)
    group_a = UserGroup(name="Group A", organization_id=org_a.id)
    group_b = UserGroup(name="Group B", organization_id=org_b.id)
    db_session.add_all([platform_group, group_a, group_b])
    db_session.flush()

    repo = GroupRepository(db_session)
    result = repo.list_groups_for_organization(org_a.id)

    # Should only contain org_a groups
    assert any(g.name == "Group A" for g in result)
    assert not any(g.name == "Group B" for g in result)
    assert not any(g.name == "Platform Group" for g in result)


def test_list_groups_for_organization_returns_empty_when_no_groups(
    db_session: Session,
) -> None:
    """list_groups_for_organization() returns empty list when organization
    has no groups."""
    org = Organization(name="Empty Org")
    db_session.add(org)
    db_session.flush()

    repo = GroupRepository(db_session)
    result = repo.list_groups_for_organization(org.id)

    assert result == []


def test_create_group_with_organization_id_sets_org_scoping(
    db_session: Session,
) -> None:
    """create_group() with organization_id parameter creates group with that
    organization_id set (not None)."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    repo = GroupRepository(db_session)
    created = repo.create_group(
        name="Org Scoped",
        description="Test group",
        organization_id=org.id,
    )
    db_session.flush()

    assert created.organization_id == org.id


def test_create_group_without_organization_id_creates_platform_group(
    db_session: Session,
) -> None:
    """create_group() without organization_id parameter creates platform-scoped
    group (organization_id is None)."""
    repo = GroupRepository(db_session)
    created = repo.create_group(
        name="Platform Scoped",
        description="Test group",
    )
    db_session.flush()

    assert created.organization_id is None


def test_sync_org_membership_group_joined_true_adds_user_to_org_admin_group(
    db_session: Session,
) -> None:
    """sync_org_membership_group(..., joined=True) adds user to org's admin group."""
    from app.modules.security.permission_catalog import ORG_ADMIN_GROUP_KEY

    org = Organization(name="Test Org Sync 1")
    db_session.add(org)
    db_session.flush()

    user = _user(db_session, "syncuser1")
    actor = _user(db_session, "syncadmin1")
    db_session.commit()

    service = _group_service(db_session)

    # Create org admin group
    admin_group = (
        db_session.query(UserGroup)
        .filter_by(organization_id=org.id, system_key=ORG_ADMIN_GROUP_KEY)
        .first()
    )
    if not admin_group:
        admin_group = UserGroup(
            name="Org Admin",
            description="Organization admin",
            is_system=True,
            system_key=ORG_ADMIN_GROUP_KEY,
            organization_id=org.id,
        )
        db_session.add(admin_group)
        db_session.flush()

    # Sync membership (joined=True)
    service.sync_org_membership_group(user.id, org.id, joined=True, actor=actor)

    # Check user is now in admin group
    user_groups = service.group_ids_for_user(user.id)
    assert admin_group.id in user_groups


def test_sync_org_membership_group_joined_false_removes_user_from_org_groups(
    db_session: Session,
) -> None:
    """sync_org_membership_group(..., joined=False) removes user from org groups."""
    from app.modules.security.permission_catalog import ORG_ADMIN_GROUP_KEY

    org = Organization(name="Test Org Sync 2")
    db_session.add(org)
    db_session.flush()

    user = _user(db_session, "syncuser2")
    actor = _user(db_session, "syncadmin2")

    # Create org admin group
    admin_group = UserGroup(
        name="Org Admin",
        description="Organization admin",
        is_system=True,
        system_key=ORG_ADMIN_GROUP_KEY,
        organization_id=org.id,
    )
    db_session.add(admin_group)
    db_session.flush()

    service = _group_service(db_session)

    # Add user to group first
    repo = GroupRepository(db_session)
    repo.replace_user_groups(user.id, {admin_group.id})
    db_session.flush()

    # Verify user is in group
    assert admin_group.id in service.group_ids_for_user(user.id)

    # Sync membership (joined=False)
    service.sync_org_membership_group(user.id, org.id, joined=False, actor=actor)

    # Check user was removed from admin group
    user_groups = service.group_ids_for_user(user.id)
    assert admin_group.id not in user_groups

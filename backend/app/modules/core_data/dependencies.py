"""Dependencies for core_data domain."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.dependencies import get_db
from app.modules.audit.dependencies import get_audit_service
from app.modules.core_data.repositories.devices import DeviceRepository
from app.modules.core_data.repositories.measurement_points import (
    MeasurementPointRepository,
)
from app.modules.core_data.repositories.organizations import OrganizationRepository
from app.modules.core_data.repositories.users import UserRepository
from app.modules.core_data.repositories.users_organizations import (
    UsersOrganizationsRepository,
)
from app.modules.core_data.repositories.water_objects import WaterObjectRepository
from app.modules.core_data.services.context import UserContextService
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.measurement_points import (
    MeasurementPointService,
)
from app.modules.core_data.services.members import MembersService
from app.modules.core_data.services.organizations import OrganizationService
from app.modules.core_data.services.users import UserService
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.security.dependencies import (
    get_permission_repo,
    get_permission_service,
)
from app.modules.security.repositories import PermissionRepository
from app.modules.security.services.permissions import PermissionService


def get_user_repo(session: Session = Depends(get_db)) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(session)


def get_user_service(
    repo: UserRepository = Depends(get_user_repo),
    permissions: PermissionService = Depends(get_permission_service),
    audit: AuditPort = Depends(get_audit_service),
) -> UserService:
    """Get user service dependency."""
    return UserService(repo, permissions, audit)


def get_organization_repo(session: Session = Depends(get_db)) -> OrganizationRepository:
    """Get organization repository dependency."""
    return OrganizationRepository(session)


def get_organization_service(
    repo: OrganizationRepository = Depends(get_organization_repo),
    perm_service: PermissionService = Depends(get_permission_service),
    audit: AuditPort = Depends(get_audit_service),
) -> OrganizationService:
    """Get organization service dependency."""
    return OrganizationService(repo, perm_service, audit)


def get_water_object_repo(session: Session = Depends(get_db)) -> WaterObjectRepository:
    """Get water object repository dependency."""
    return WaterObjectRepository(session)


def get_water_object_service(
    repo: WaterObjectRepository = Depends(get_water_object_repo),
    org_repo: OrganizationRepository = Depends(get_organization_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> WaterObjectService:
    """Get water object service dependency."""
    return WaterObjectService(repo, org_repo, audit)


def get_device_repo(session: Session = Depends(get_db)) -> DeviceRepository:
    """Get device repository dependency."""
    return DeviceRepository(session)


def get_device_service(
    repo: DeviceRepository = Depends(get_device_repo),
    water_object_repo: WaterObjectRepository = Depends(get_water_object_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> DeviceService:
    """Get device service dependency."""
    return DeviceService(repo, water_object_repo, audit)


def get_measurement_point_repo(
    session: Session = Depends(get_db),
) -> MeasurementPointRepository:
    """Get measurement point repository dependency."""
    return MeasurementPointRepository(session)


def get_measurement_point_service(
    repo: MeasurementPointRepository = Depends(get_measurement_point_repo),
    device_repo: DeviceRepository = Depends(get_device_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> MeasurementPointService:
    """Get measurement point service dependency."""
    return MeasurementPointService(repo, device_repo, audit)


def get_users_organizations_repo(
    session: Session = Depends(get_db),
) -> UsersOrganizationsRepository:
    """Get users-organizations repository dependency."""
    return UsersOrganizationsRepository(session)


def get_members_service(
    repo: UsersOrganizationsRepository = Depends(get_users_organizations_repo),
    user_service: UserService = Depends(get_user_service),
    perm_repo: PermissionRepository = Depends(get_permission_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> MembersService:
    """Get members service dependency."""
    return MembersService(repo, user_service, perm_repo, audit)


def get_user_context_service(
    members_service: MembersService = Depends(get_members_service),
    permissions: PermissionService = Depends(get_permission_service),
) -> UserContextService:
    """Get user context service dependency."""
    return UserContextService(members_service, permissions)

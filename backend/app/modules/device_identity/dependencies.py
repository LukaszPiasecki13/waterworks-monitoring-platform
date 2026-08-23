"""Dependency wiring for device_identity module."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.audit import AuditPort
from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.errors import NotFoundError
from app.modules.audit.dependencies import get_audit_service
from app.modules.core_data.dependencies import (
    get_device_service,
    get_water_object_service,
)
from app.modules.core_data.models.device import Device
from app.modules.core_data.services.devices import DeviceService
from app.modules.core_data.services.water_objects import WaterObjectService
from app.modules.device_identity.repositories.device_activation_codes import (
    DeviceActivationCodeRepository,
)
from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)
from app.modules.device_identity.services.activation_codes import (
    DeviceActivationCodeService,
)
from app.modules.device_identity.services.claims import DeviceClaimService
from app.modules.device_identity.services.device_auth import DeviceAuthService
from app.modules.device_identity.services.provisioning import (
    DeviceProvisioningService,
)
from app.modules.security.dependencies import get_token_service
from app.modules.security.services.token import TokenService

bearer_scheme = HTTPBearer(auto_error=False)


def get_credential_repo(
    session: Session = Depends(get_db),
) -> DeviceCredentialRepository:
    """Get device credential repository dependency."""
    return DeviceCredentialRepository(session)


def get_activation_code_repo(
    session: Session = Depends(get_db),
) -> DeviceActivationCodeRepository:
    """Get device activation code repository dependency."""
    return DeviceActivationCodeRepository(session)


def get_provisioning_service(
    repo: DeviceCredentialRepository = Depends(get_credential_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> DeviceProvisioningService:
    """Get provisioning service dependency."""
    return DeviceProvisioningService(repo, audit)


def get_claim_service(
    water_object_service: WaterObjectService = Depends(get_water_object_service),
    device_service: DeviceService = Depends(get_device_service),
) -> DeviceClaimService:
    """Get claim service dependency."""
    return DeviceClaimService(water_object_service, device_service)


def get_device_auth_service(
    credential_repo: DeviceCredentialRepository = Depends(get_credential_repo),
    device_service: DeviceService = Depends(get_device_service),
    token_service: TokenService = Depends(get_token_service),
    audit: AuditPort = Depends(get_audit_service),
) -> DeviceAuthService:
    """Get device auth service dependency."""
    settings = get_settings()
    return DeviceAuthService(
        credential_repo,
        device_service,
        token_service,
        audit,
        settings.device_challenge_expire_seconds,
    )


def get_activation_code_service(
    code_repo: DeviceActivationCodeRepository = Depends(get_activation_code_repo),
    credential_repo: DeviceCredentialRepository = Depends(get_credential_repo),
    audit: AuditPort = Depends(get_audit_service),
) -> DeviceActivationCodeService:
    """Get activation code service dependency."""
    settings = get_settings()
    return DeviceActivationCodeService(code_repo, credential_repo, audit, settings)


def get_current_device(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    device_service: DeviceService = Depends(get_device_service),
    token_service: TokenService = Depends(get_token_service),
) -> Device:
    """Get current authenticated device from Authorization bearer token.

    Raises 401 if token is missing, invalid, or device is inactive.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = token_service.decode_token(token)
    if not payload or payload.get("type") != "device":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    device_id = payload.get("sub")
    if not device_id or not isinstance(device_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        device_id = UUID(device_id)
    except ValueError, TypeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    try:
        device = device_service.find_by_id_unscoped(device_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device not found",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return device

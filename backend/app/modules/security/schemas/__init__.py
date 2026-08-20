"""Security schemas."""

from app.modules.core_data.schemas.users import UserResponse

from .auth import (
    LoginRequest,
    ProfileUpdateRequest,
    TokenRefreshRequest,
    TokenResponse,
)
from .permissions import (
    GroupIdsRequest,
    MyPermissionsResponse,
    PermissionCodesRequest,
    PermissionResponse,
    UserGroupCreateRequest,
    UserGroupResponse,
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
    UserIdsRequest,
)

__all__ = [
    "GroupIdsRequest",
    "LoginRequest",
    "MyPermissionsResponse",
    "PermissionCodesRequest",
    "PermissionResponse",
    "ProfileUpdateRequest",
    "TokenRefreshRequest",
    "TokenResponse",
    "UserGroupCreateRequest",
    "UserGroupResponse",
    "UserGroupSaveRequest",
    "UserGroupUpdateRequest",
    "UserIdsRequest",
    "UserResponse",
]

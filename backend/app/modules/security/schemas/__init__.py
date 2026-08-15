"""Security schemas."""

from .auth import (
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
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
    "RegisterRequest",
    "TokenRefreshRequest",
    "TokenResponse",
    "UserGroupCreateRequest",
    "UserGroupResponse",
    "UserGroupSaveRequest",
    "UserGroupUpdateRequest",
    "UserIdsRequest",
    "UserResponse",
]

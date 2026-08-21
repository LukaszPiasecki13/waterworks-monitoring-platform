"""Security schemas."""

from app.modules.core_data.schemas.users import UserResponse

from .auth import (
    LoginRequest,
    ProfileUpdateRequest,
    TokenRefreshRequest,
    TokenResponse,
)
from .groups import (
    GroupIdsRequest,
    PermissionCodesRequest,
    UserGroupCreateRequest,
    UserGroupResponse,
    UserGroupSaveRequest,
    UserGroupUpdateRequest,
    UserIdsRequest,
)
from .permissions import MyPermissionsResponse, PermissionResponse

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

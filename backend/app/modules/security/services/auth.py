from uuid import UUID

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
)
from app.modules.core_data.audit_state import user_audit_state
from app.modules.core_data.models import User
from app.modules.core_data.repositories.users import UserRepository
from app.modules.security.schemas import (
    LoginRequest,
    ProfileUpdateRequest,
    TokenResponse,
)
from app.modules.security.services.password import (
    burn_password_verification,
    hash_password,
    verify_password,
)
from app.modules.security.services.permissions import PermissionService

from .token import TokenService


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        token_service: TokenService,
        permissions: PermissionService,
        audit: AuditPort,
    ):
        self.repo = repo
        self.token_service = token_service
        self.permissions = permissions
        self.audit = audit

    def _state(self, user: User) -> dict:
        return user_audit_state(user)

    def _record_user(
        self,
        action: str,
        user: User,
        old_state: dict,
        new_state: dict,
        *,
        password_changed: bool = False,
    ) -> None:
        changes = calculate_delta(old_state, new_state)
        if password_changed:
            changes["password"] = {"old": "[ukryte]", "new": "[zmieniono]"}
        self.audit.record(
            AuditEntry(
                entity_type=EntityType.CORE_DATA_USER.value,
                entity_id=str(user.id),
                action=action,
                actor_id=str(user.id),
                actor_display_name=user.email,
                changes=changes,
            )
        )

    def _issue_tokens(self, user: User) -> TokenResponse:
        sub = {"sub": str(user.id)}
        access = self.token_service.create_access_token(sub)
        refresh = self.token_service.create_refresh_token(sub)
        return TokenResponse(access=access, refresh=refresh)

    def register(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """Register new user."""
        with self.repo.transaction():
            # Normalize inputs for consistent lookups
            normalized_username = username.strip().lower()
            normalized_email = email.strip().lower()

            # Check if user already exists
            if self.repo.get_by_username(normalized_username):
                raise ConflictError(f"Username '{username}' already exists")
            if self.repo.get_by_email(normalized_email):
                raise ConflictError(f"Email '{email}' already exists")

            user = self.repo.create(
                username=normalized_username,
                email=normalized_email,
                hashed_password=hash_password(password),
                first_name=first_name,
                last_name=last_name,
            )
            self.repo.flush()
            self.repo.refresh(user)
            self.permissions.assign_default_group(user, actor=user)
            self._record_user("REGISTER", user, {}, self._state(user))
            return user

    def login(self, data: LoginRequest) -> TokenResponse:
        """Login user - supports username or email."""
        identifier = data.username.strip().lower()

        # Try to find by username first, then by email
        user = self.repo.get_by_username(identifier)
        if not user:
            user = self.repo.get_by_email(identifier)

        if not user:
            burn_password_verification(data.password)
            raise AuthenticationError("Invalid credentials")

        if not user.is_active or not verify_password(
            data.password, user.hashed_password
        ):
            raise AuthenticationError("Invalid credentials")

        return self._issue_tokens(user)

    def update_profile(self, user: User, data: ProfileUpdateRequest) -> User:
        """Update the current user's own profile, optionally changing the password."""
        with self.repo.transaction() as tx:
            if data.new_password:
                if not data.current_password:
                    raise BadRequestError("Podaj obecne hasło, aby je zmienić.")
                if not verify_password(data.current_password, user.hashed_password):
                    raise BadRequestError("Nieprawidłowe obecne hasło.")

            if data.email and data.email != user.email:
                normalized_email = data.email.strip().lower()
                existing = self.repo.get_by_email(normalized_email)
                if existing and existing.id != user.id:
                    raise ConflictError(f"Email '{data.email}' already exists")
                data.email = normalized_email

            old_state = self._state(user)
            user = self.repo.update(
                user,
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
                hashed_password=(
                    hash_password(data.new_password) if data.new_password else None
                ),
            )
            self.repo.flush()
            self.repo.refresh(user)
            new_state = self._state(user)
            changes = calculate_delta(old_state, new_state)
            if data.new_password:
                changes["password"] = {
                    "old": "[ukryte]",
                    "new": "[zmieniono]",
                }
            if not changes:
                tx.skip_audit()
                return user
            self._record_user(
                "PROFILE_UPDATE",
                user,
                old_state,
                new_state,
                password_changed=bool(data.new_password),
            )
            return user

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self.token_service.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise AuthenticationError("Invalid refresh token")
        try:
            user_id = UUID(user_id)
        except (ValueError, TypeError) as err:
            raise AuthenticationError("Invalid refresh token") from err
        user = self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found")
        return self._issue_tokens(user)

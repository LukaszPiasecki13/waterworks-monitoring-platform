"""User management service."""

from app.core.audit import AuditEntry, AuditPort, EntityType, calculate_delta
from app.core.errors import BadRequestError, ConflictError, NotFoundError
from app.modules.core_data.audit_state import user_audit_state
from app.modules.core_data.models.user import User
from app.modules.core_data.repositories.users import UserRepository
from app.modules.core_data.schemas.users import UserCreateRequest, UserUpdateRequest
from app.modules.security.services.password import hash_password
from app.modules.security.services.permissions import PermissionService


class UserService:
    """Service for user management operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        permissions: PermissionService,
        audit: AuditPort,
    ):
        self.user_repo = user_repo
        self.permissions = permissions
        self.audit = audit

    def _state(self, user: User) -> dict:
        return user_audit_state(user)

    def _record(
        self,
        action: str,
        user: User,
        actor: User,
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
                actor_id=str(actor.id),
                actor_display_name=actor.email,
                changes=changes,
            )
        )

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID or raise NotFoundError."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user

    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
    ):
        """List users with pagination and filters."""
        users = self.user_repo.list_all(
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            is_active=is_active,
        )
        count = self.user_repo.count(
            search=search,
            status=status,
            is_active=is_active,
        )
        return users, count

    def create_user(
        self,
        request: UserCreateRequest,
        *,
        actor: User,
    ) -> User:
        """Create a user from the admin panel."""
        try:
            normalized_username = request.username.strip().lower()
            normalized_email = str(request.email).strip().lower()

            if self.user_repo.get_by_username(normalized_username):
                raise ConflictError(f"Username '{request.username}' already exists")
            if self.user_repo.get_by_email(normalized_email):
                raise ConflictError(f"Email '{request.email}' already exists")

            user = self.user_repo.create(
                username=normalized_username,
                email=normalized_email,
                hashed_password=hash_password(request.password),
                first_name=request.first_name,
                last_name=request.last_name,
                status=request.status,
                is_active=request.is_active,
            )
            self.user_repo.flush()
            self.user_repo.refresh(user)
            self.permissions.assign_default_group(user, actor=actor)
            self._record("CREATE", user, actor, {}, self._state(user))
            self.user_repo.commit()
            return user
        except Exception:
            self.user_repo.rollback()
            raise

    def update_user(
        self, user_id: int, request: UserUpdateRequest, actor: User
    ) -> User:
        """Update a user from the admin panel."""
        try:
            user = self.get_user_by_id(user_id)
            old_state = self._state(user)
            username = (
                request.username.strip().lower()
                if request.username is not None
                else None
            )
            email = (
                str(request.email).strip().lower()
                if request.email is not None
                else None
            )

            if username is not None:
                existing = self.user_repo.get_by_username(username)
                if existing and existing.id != user.id:
                    raise ConflictError(f"Username '{request.username}' already exists")

            if email is not None:
                existing = self.user_repo.get_by_email(email)
                if existing and existing.id != user.id:
                    raise ConflictError(f"Email '{request.email}' already exists")

            password = request.password
            user = self.user_repo.update(
                user,
                username=username,
                email=email,
                first_name=request.first_name,
                last_name=request.last_name,
                status=request.status,
                is_active=request.is_active,
                hashed_password=hash_password(password) if password else None,
            )
            self.user_repo.flush()
            self.user_repo.refresh(user)
            new_state = self._state(user)
            changes = calculate_delta(old_state, new_state)
            if password:
                changes["password"] = {
                    "old": "[ukryte]",
                    "new": "[zmieniono]",
                }
            if not changes:
                self.user_repo.commit(skip_audit=True)
                return user
            self._record(
                "UPDATE",
                user,
                actor,
                old_state,
                new_state,
                password_changed=bool(password),
            )
            self.user_repo.commit()
            return user
        except Exception:
            self.user_repo.rollback()
            raise

    def delete_user(self, user_id: int, actor: User) -> None:
        """Delete a user from the admin panel."""
        if actor.id == user_id:
            raise BadRequestError("You cannot delete your own account")

        try:
            user = self.get_user_by_id(user_id)
            old_state = self._state(user)
            self.user_repo.delete(user)
            self._record("DELETE", user, actor, old_state, {})
            self.user_repo.commit()
        except Exception:
            self.user_repo.rollback()
            raise

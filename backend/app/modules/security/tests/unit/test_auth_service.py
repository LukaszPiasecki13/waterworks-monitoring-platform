from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import AuthenticationError, BadRequestError, ConflictError
from app.modules.security.schemas import LoginRequest, ProfileUpdateRequest
from app.modules.security.services.auth import AuthService


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def repo(session: MagicMock) -> MagicMock:
    repository = MagicMock()
    repository.session = session
    return repository


@pytest.fixture
def token_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(
    repo: MagicMock,
    token_service: MagicMock,
    session: MagicMock,
) -> AuthService:
    repo.flush = session.flush
    repo.refresh = session.refresh
    repo.commit = session.commit
    repo.rollback = session.rollback
    permissions = MagicMock()
    permissions.group_ids_for_user.return_value = []
    return AuthService(repo, token_service, permissions, MagicMock())


def test_register_rolls_back_when_username_exists(
    service: AuthService,
    repo: MagicMock,
    session: MagicMock,
) -> None:
    repo.get_by_username.return_value = SimpleNamespace(id=1)

    with pytest.raises(ConflictError) as exc_info:
        service.register(
            username="existing",
            email="new@example.com",
            password="StrongPass123",
        )

    assert exc_info.value.status_code == 409
    repo.create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once()



def test_login_uses_username_then_email_and_issues_tokens(
    service: AuthService,
    repo: MagicMock,
    token_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = SimpleNamespace(id=42, is_active=True, hashed_password="stored-hash")
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = user
    token_service.create_access_token.return_value = "access-token"
    token_service.create_refresh_token.return_value = "refresh-token"
    monkeypatch.setattr(
        "app.modules.security.services.auth.verify_password",
        lambda plain, hashed: plain == "StrongPass123" and hashed == "stored-hash",
    )

    token = service.login(
        LoginRequest(username=" USER@EXAMPLE.COM ", password="StrongPass123")
    )

    assert token.access == "access-token"
    assert token.refresh == "refresh-token"
    repo.get_by_username.assert_called_once_with("user@example.com")
    repo.get_by_email.assert_called_once_with("user@example.com")
    token_service.create_access_token.assert_called_once_with({"sub": "42"})
    token_service.create_refresh_token.assert_called_once_with({"sub": "42"})


def test_login_rejects_invalid_credentials(
    service: AuthService,
    repo: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    monkeypatch.setattr(
        "app.modules.security.services.auth.verify_password",
        lambda plain, hashed: True,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        service.login(LoginRequest(username="user@example.com", password="bad"))

    assert exc_info.value.status_code == 401


def test_update_profile_requires_current_password_for_password_change(
    service: AuthService,
    session: MagicMock,
) -> None:
    user = SimpleNamespace(
        id=1,
        email="user@example.com",
        hashed_password="stored-hash",
    )

    with pytest.raises(BadRequestError) as exc_info:
        service.update_profile(
            user,
            ProfileUpdateRequest(new_password="NewStrongPass123"),
        )

    assert exc_info.value.status_code == 400
    session.rollback.assert_called_once()


def test_refresh_rejects_non_refresh_token(
    service: AuthService,
    token_service: MagicMock,
) -> None:
    token_service.decode_token.return_value = {"sub": "42", "type": "access"}

    with pytest.raises(AuthenticationError) as exc_info:
        service.refresh("access-token")

    assert exc_info.value.status_code == 401

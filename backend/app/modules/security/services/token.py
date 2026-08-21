from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt


class TokenService:
    """Encapsulates token creation/decoding and accepts configuration via
    constructor so the service can be injected and tested without importing
    application settings at module import time.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 120,
        refresh_token_expire_days: int = 1,
        device_token_expire_hours: int = 36,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_token_expire_minutes
        self._refresh_expire_days = refresh_token_expire_days
        self._device_expire_hours = device_token_expire_hours

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta or timedelta(minutes=self._access_expire_minutes)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self._refresh_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def create_device_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> tuple[str, datetime]:
        """Create a device session token.

        Returns:
            Tuple of (token, expires_at)
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta or timedelta(hours=self._device_expire_hours)
        )
        to_encode.update({"exp": expire, "type": "device"})
        token = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return token, expire

    def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            return None

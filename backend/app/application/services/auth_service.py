"""Authentication application service.

Orchestrates the auth use-cases against the repository interfaces.
Depends only on abstractions (UserRepository, RefreshTokenRepository)
— never imports SQLAlchemy directly — so this class is unit-testable
with fake repositories.
"""

import uuid
from datetime import datetime, timezone

from app.core import security
from app.core.config import settings
from app.core.exceptions import AuthenticationError, NotFoundError, ValidationError
from app.core.security import TokenType
from app.core.token_hashing import hash_token
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user import User
from app.workers.tasks import send_password_reset_email_task, send_verification_email_task


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self._users = user_repository
        self._refresh_tokens = refresh_token_repository

    async def register(self, *, email: str, password: str, full_name: str) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ValidationError("An account with this email already exists")

        hashed_password = security.hash_password(password)
        user = await self._users.create(
            email=email, hashed_password=hashed_password, full_name=full_name
        )

        verification_token = security.create_email_verification_token(user.id)
        send_verification_email_task.delay(
            to_email=user.email, full_name=user.full_name, token=verification_token
        )
        return user

    async def login(
        self, *, email: str, password: str, device_info: str | None = None
    ) -> tuple[str, str, int]:
        """Returns (access_token, refresh_token, expires_in_seconds)."""
        user = await self._users.get_by_email(email)
        if user is None or not security.verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("This account has been deactivated")

        user.last_login_at = datetime.now(timezone.utc)
        await self._users.update(user)

        access_token = security.create_access_token(user.id)
        raw_refresh_token, _, expires_at = security.create_refresh_token(user.id)
        await self._refresh_tokens.create(
            user_id=user.id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=expires_at,
            device_info=device_info,
        )

        expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return access_token, raw_refresh_token, expires_in

    async def refresh_access_token(self, *, raw_refresh_token: str) -> tuple[str, str, int]:
        """Validates the refresh token, rotates it, and returns a new pair.

        Rotation (issuing a brand new refresh token and revoking the old
        one on every use) limits the damage window if a refresh token
        is ever stolen.
        """
        payload = security.decode_token(raw_refresh_token, TokenType.REFRESH)
        user_id = uuid.UUID(payload["sub"])

        stored = await self._refresh_tokens.get_by_hash(hash_token(raw_refresh_token))
        if stored is None or stored.revoked or stored.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Refresh token is invalid or has expired")

        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Account is no longer active")

        await self._refresh_tokens.revoke(stored)

        access_token = security.create_access_token(user.id)
        new_raw_refresh_token, _, expires_at = security.create_refresh_token(user.id)
        await self._refresh_tokens.create(
            user_id=user.id,
            token_hash=hash_token(new_raw_refresh_token),
            expires_at=expires_at,
            device_info=stored.device_info,
        )

        expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return access_token, new_raw_refresh_token, expires_in

    async def logout(self, *, raw_refresh_token: str) -> None:
        stored = await self._refresh_tokens.get_by_hash(hash_token(raw_refresh_token))
        if stored is not None and not stored.revoked:
            await self._refresh_tokens.revoke(stored)

    async def forgot_password(self, *, email: str) -> None:
        """Always succeeds silently even if the email doesn't exist.

        This prevents account enumeration — an attacker can't use this
        endpoint to discover which emails have accounts.
        """
        user = await self._users.get_by_email(email)
        if user is None:
            return
        reset_token = security.create_password_reset_token(user.id)
        send_password_reset_email_task.delay(
            to_email=user.email, full_name=user.full_name, token=reset_token
        )

    async def reset_password(self, *, token: str, new_password: str) -> None:
        payload = security.decode_token(token, TokenType.PASSWORD_RESET)
        user_id = uuid.UUID(payload["sub"])

        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))

        user.hashed_password = security.hash_password(new_password)
        await self._users.update(user)
        # Force re-login on every device after a password reset.
        await self._refresh_tokens.revoke_all_for_user(user.id)

    async def verify_email(self, *, token: str) -> None:
        payload = security.decode_token(token, TokenType.EMAIL_VERIFICATION)
        user_id = uuid.UUID(payload["sub"])

        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))

        user.is_verified = True
        await self._users.update(user)

    async def resend_verification(self, *, email: str) -> None:
        user = await self._users.get_by_email(email)
        if user is None or user.is_verified:
            return
        verification_token = security.create_email_verification_token(user.id)
        send_verification_email_task.delay(
            to_email=user.email, full_name=user.full_name, token=verification_token
        )

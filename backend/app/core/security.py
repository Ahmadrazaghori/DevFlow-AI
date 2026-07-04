"""Security primitives: password hashing and JWT handling.

All token creation/verification funnels through this module so there
is exactly one place that understands the JWT claim structure and
signing key. Argon2 parameters come from Settings so they can be
tuned per-environment without code changes.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError

_password_hasher = PasswordHasher(
    time_cost=settings.ARGON2_TIME_COST,
    memory_cost=settings.ARGON2_MEMORY_COST,
    parallelism=settings.ARGON2_PARALLELISM,
)


def hash_password(plain_password: str) -> str:
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


def _create_token(
    subject: uuid.UUID,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, uuid.UUID, datetime]:
    """Build and sign a JWT. Returns (token, jti, expires_at)."""
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = uuid.uuid4()

    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": expires_at,
        "iss": settings.JWT_ISSUER,
        "jti": str(jti),
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expires_at


def create_access_token(user_id: uuid.UUID) -> str:
    token, _, _ = _create_token(
        user_id,
        TokenType.ACCESS,
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return token


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, uuid.UUID, datetime]:
    return _create_token(
        user_id,
        TokenType.REFRESH,
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_verification_token(user_id: uuid.UUID) -> str:
    token, _, _ = _create_token(user_id, TokenType.EMAIL_VERIFICATION, timedelta(hours=24))
    return token


def create_password_reset_token(user_id: uuid.UUID) -> str:
    token, _, _ = _create_token(user_id, TokenType.PASSWORD_RESET, timedelta(minutes=30))
    return token


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """Decode and validate a JWT, enforcing the expected `type` claim.

    Raises TokenExpiredError / TokenInvalidError (never a raw jwt exception)
    so the API layer only has to handle our own exception hierarchy.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError() from exc

    if payload.get("type") != expected_type.value:
        raise TokenInvalidError()

    return payload

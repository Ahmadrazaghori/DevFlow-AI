"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.v1.deps import get_auth_service, get_current_active_user, get_device_info
from app.application.services.auth_service import AuthService
from app.core.main_limiter import limiter
from app.infrastructure.database.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await auth_service.register(
        email=body.email, password=body.password, full_name=body.full_name
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse, summary="Exchange credentials for tokens")
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    device_info: Annotated[str | None, Depends(get_device_info)],
) -> TokenResponse:
    access_token, refresh_token, expires_in = await auth_service.login(
        email=body.email, password=body.password, device_info=device_info
    )
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenResponse, summary="Rotate refresh token, issue new access token")
async def refresh(
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    access_token, refresh_token, expires_in = await auth_service.refresh_access_token(
        raw_refresh_token=body.refresh_token
    )
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, expires_in=expires_in
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Revoke a refresh token (log out this device)",
)
async def logout(
    body: LogoutRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.logout(raw_refresh_token=body.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset email",
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.forgot_password(email=body.email)
    return MessageResponse(
        message="If an account with that email exists, a reset link has been sent"
    )


@router.post(
    "/reset-password", response_model=MessageResponse, summary="Set a new password using a reset token"
)
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.reset_password(token=body.token, new_password=body.new_password)
    return MessageResponse(message="Password has been reset successfully")


@router.post("/verify-email", response_model=MessageResponse, summary="Confirm an email address")
async def verify_email(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.verify_email(token=body.token)
    return MessageResponse(message="Email verified successfully")


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    summary="Resend the email verification link",
)
@limiter.limit("5/minute")
async def resend_verification(
    request: Request,
    body: ResendVerificationRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    await auth_service.resend_verification(email=body.email)
    return MessageResponse(message="If that account needs verification, an email has been sent")


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)

"""Application-wide exception hierarchy.

Domain/application code raises these exceptions instead of HTTPException
directly, keeping business logic framework-agnostic. The API layer
translates them into proper HTTP responses via exception handlers
registered in app.main.
"""


class DevFlowError(Exception):
    """Base class for all application-raised errors."""

    def __init__(self, message: str, *, code: str = "internal_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DevFlowError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: str | int | None = None) -> None:
        message = f"{resource} not found" + (f" (id={identifier})" if identifier else "")
        super().__init__(message, code="not_found")


class AlreadyExistsError(DevFlowError):
    """Raised when attempting to create a resource that violates a uniqueness constraint."""

    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            f"{resource} with {field}='{value}' already exists",
            code="already_exists",
        )


class ValidationError(DevFlowError):
    """Raised for business-rule validation failures not covered by Pydantic schema validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class AuthenticationError(DevFlowError):
    """Raised when credentials are invalid or a token cannot be verified."""

    def __init__(self, message: str = "Invalid authentication credentials") -> None:
        super().__init__(message, code="authentication_error")


class AuthorizationError(DevFlowError):
    """Raised when an authenticated user lacks permission for an action."""

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message, code="authorization_error")


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired")


class TokenInvalidError(AuthenticationError):
    """Raised when a JWT is malformed or fails signature verification."""

    def __init__(self) -> None:
        super().__init__("Token is invalid")


class RateLimitExceededError(DevFlowError):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, code="rate_limit_exceeded")


class ExternalServiceError(DevFlowError):
    """Raised when a call to an external service (Anthropic API, SMTP, etc.) fails."""

    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service} error: {message}", code="external_service_error")

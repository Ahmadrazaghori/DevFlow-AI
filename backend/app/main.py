"""DevFlow AI backend entrypoint.

Application factory pattern: `create_app()` builds and returns a fully
configured FastAPI instance. This keeps app construction testable
(tests can build isolated app instances) and avoids import-time
side effects.
"""

import time
import uuid
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    DevFlowError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import configure_logging, get_logger
from app.core.main_limiter import limiter
from app.infrastructure.database.session import check_database_connection

configure_logging()
logger = get_logger(__name__)

_EXCEPTION_STATUS_MAP: dict[type[DevFlowError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup", environment=settings.APP_ENV)
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-Powered Software Engineering & DevOps Management Platform. "
            "Provides project/sprint management plus AI-driven requirement "
            "analysis, documentation generation, code review, and bug detection."
        ),
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_middleware(app)
    _register_exception_handlers(app)
    _register_routes(app)

    return app


def _register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "http_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    @app.middleware("http")
    async def secure_headers_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DevFlowError)
    async def devflow_exception_handler(request: Request, exc: DevFlowError) -> ORJSONResponse:
        status_code = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(
            "handled_exception",
            error_code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return ORJSONResponse(
            status_code=status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.exception("unhandled_exception", path=request.url.path)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            },
        )


def _register_routes(app: FastAPI) -> None:
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> ORJSONResponse:
        db_healthy = await check_database_connection()
        healthy = db_healthy
        return ORJSONResponse(
            status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "healthy" if healthy else "unhealthy",
                "checks": {"database": "up" if db_healthy else "down"},
            },
        )

    # Versioned API routers are mounted here as they are implemented, e.g.:
    from app.api.v1.router import api_router

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)


app = create_app()

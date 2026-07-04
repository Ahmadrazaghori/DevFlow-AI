"""Shared FastAPI dependencies for the v1 API.

Repositories and services are constructed per-request from the
request-scoped DB session (see get_db_session), so each request gets
its own unit of work with no state leaking across requests.
"""

import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.application.services.label_service import LabelService
from app.application.services.organization_service import OrganizationService
from app.application.services.project_service import ProjectService
from app.application.services.sprint_service import SprintService
from app.application.services.task_service import TaskService
from app.core.exceptions import AuthorizationError
from app.core.security import TokenType, decode_token
from app.domain.repositories.label_repository import LabelRepository, TaskCommentRepository
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.sprint_repository import SprintRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.label_repository import (
    SQLAlchemyLabelRepository,
    SQLAlchemyTaskCommentRepository,
)
from app.infrastructure.database.repositories.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from app.infrastructure.database.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.database.repositories.refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.database.repositories.sprint_repository import SQLAlchemySprintRepository
from app.infrastructure.database.repositories.task_repository import SQLAlchemyTaskRepository
from app.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.database.session import get_db_session

_bearer_scheme = HTTPBearer(auto_error=True)


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_refresh_token_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)


async def get_organization_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrganizationRepository:
    return SQLAlchemyOrganizationRepository(session)


async def get_project_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProjectRepository:
    return SQLAlchemyProjectRepository(session)


async def get_sprint_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SprintRepository:
    return SQLAlchemySprintRepository(session)


async def get_task_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaskRepository:
    return SQLAlchemyTaskRepository(session)


async def get_label_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LabelRepository:
    return SQLAlchemyLabelRepository(session)


async def get_task_comment_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaskCommentRepository:
    return SQLAlchemyTaskCommentRepository(session)


async def get_organization_service(
    org_repository: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> OrganizationService:
    return OrganizationService(org_repository, user_repository)


async def get_project_service(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    org_repository: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ProjectService:
    return ProjectService(project_repository, org_repository, user_repository)


async def get_sprint_service(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> SprintService:
    return SprintService(sprint_repository, project_repository)


async def get_task_service(
    task_repository: Annotated[TaskRepository, Depends(get_task_repository)],
    comment_repository: Annotated[TaskCommentRepository, Depends(get_task_comment_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> TaskService:
    return TaskService(task_repository, comment_repository, project_repository)


async def get_label_service(
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> LabelService:
    return LabelService(label_repository, project_repository)


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repository: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
) -> AuthService:
    return AuthService(user_repository, refresh_token_repository)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    payload = decode_token(credentials.credentials, TokenType.ACCESS)
    user_id = uuid.UUID(payload["sub"])

    user = await user_repository.get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthorizationError("User account is not active")
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


async def require_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        raise AuthorizationError("This action requires administrator privileges")
    return current_user


def get_device_info(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent")
    return user_agent[:255] if user_agent else None

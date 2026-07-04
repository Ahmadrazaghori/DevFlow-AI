"""Project endpoints.

Creation and listing are nested under an organization
(/organizations/{organization_id}/projects); direct project operations
use the flat /projects/{project_id} path since a project ID alone is
enough to identify it (no need to repeat the organization in the URL).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_active_user, get_project_service
from app.application.services.project_service import ProjectService
from app.infrastructure.database.models.user import User
from app.schemas.project import (
    AddProjectMemberRequest,
    ProjectCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)

org_projects_router = APIRouter(prefix="/organizations/{organization_id}/projects", tags=["Projects"])
projects_router = APIRouter(prefix="/projects", tags=["Projects"])


@org_projects_router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    organization_id: uuid.UUID,
    body: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    project = await project_service.create_project(
        current_user=current_user,
        organization_id=organization_id,
        name=body.name,
        key=body.key,
        description=body.description,
        repository_url=body.repository_url,
    )
    return ProjectResponse.model_validate(project)


@org_projects_router.get("", response_model=list[ProjectResponse])
async def list_projects(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> list[ProjectResponse]:
    projects = await project_service.list_projects(
        current_user=current_user, organization_id=organization_id
    )
    return [ProjectResponse.model_validate(p) for p in projects]


@projects_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    project = await project_service.get_project(current_user=current_user, project_id=project_id)
    return ProjectResponse.model_validate(project)


@projects_router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    project = await project_service.update_project(
        current_user=current_user,
        project_id=project_id,
        name=body.name,
        description=body.description,
        status=body.status,
        repository_url=body.repository_url,
    )
    return ProjectResponse.model_validate(project)


@projects_router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: uuid.UUID,
    body: AddProjectMemberRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectMemberResponse:
    member = await project_service.add_member(
        current_user=current_user, project_id=project_id, email=body.email, role=body.role
    )
    return ProjectMemberResponse.model_validate(member)


@projects_router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
async def list_project_members(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> list[ProjectMemberResponse]:
    members = await project_service.list_members(current_user=current_user, project_id=project_id)
    return [ProjectMemberResponse.model_validate(m) for m in members]

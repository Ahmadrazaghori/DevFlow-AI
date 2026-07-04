"""Sprint endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_active_user, get_sprint_service
from app.application.services.sprint_service import SprintService
from app.infrastructure.database.models.user import User
from app.schemas.sprint import SprintCreate, SprintResponse, SprintUpdate

project_sprints_router = APIRouter(prefix="/projects/{project_id}/sprints", tags=["Sprints"])
sprints_router = APIRouter(prefix="/sprints", tags=["Sprints"])


@project_sprints_router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    project_id: uuid.UUID,
    body: SprintCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    sprint_service: Annotated[SprintService, Depends(get_sprint_service)],
) -> SprintResponse:
    sprint = await sprint_service.create_sprint(
        current_user=current_user,
        project_id=project_id,
        name=body.name,
        goal=body.goal,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    return SprintResponse.model_validate(sprint)


@project_sprints_router.get("", response_model=list[SprintResponse])
async def list_sprints(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    sprint_service: Annotated[SprintService, Depends(get_sprint_service)],
) -> list[SprintResponse]:
    sprints = await sprint_service.list_sprints(current_user=current_user, project_id=project_id)
    return [SprintResponse.model_validate(s) for s in sprints]


@sprints_router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    sprint_service: Annotated[SprintService, Depends(get_sprint_service)],
) -> SprintResponse:
    sprint = await sprint_service.get_sprint(current_user=current_user, sprint_id=sprint_id)
    return SprintResponse.model_validate(sprint)


@sprints_router.patch("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: uuid.UUID,
    body: SprintUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    sprint_service: Annotated[SprintService, Depends(get_sprint_service)],
) -> SprintResponse:
    sprint = await sprint_service.update_sprint(
        current_user=current_user,
        sprint_id=sprint_id,
        name=body.name,
        goal=body.goal,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    return SprintResponse.model_validate(sprint)


@sprints_router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    sprint_service: Annotated[SprintService, Depends(get_sprint_service)],
) -> None:
    await sprint_service.delete_sprint(current_user=current_user, sprint_id=sprint_id)

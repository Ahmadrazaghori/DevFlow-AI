"""Task, Label, and TaskComment endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import get_current_active_user, get_label_service, get_task_service
from app.application.services.label_service import LabelService
from app.application.services.task_service import TaskService
from app.infrastructure.database.models.enums import TaskPriority, TaskStatus
from app.infrastructure.database.models.user import User
from app.schemas.task import (
    LabelCreate,
    LabelResponse,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

project_tasks_router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])
project_labels_router = APIRouter(prefix="/projects/{project_id}/labels", tags=["Labels"])


@project_tasks_router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: uuid.UUID,
    body: TaskCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = await task_service.create_task(
        current_user=current_user,
        project_id=project_id,
        title=body.title,
        description=body.description,
        task_type=body.task_type,
        priority=body.priority,
        story_points=body.story_points,
        sprint_id=body.sprint_id,
        assignee_id=body.assignee_id,
        due_date=body.due_date,
        label_ids=body.label_ids,
    )
    return TaskResponse.model_validate(task)


@project_tasks_router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    sprint_id: Annotated[uuid.UUID | None, Query()] = None,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: Annotated[TaskPriority | None, Query()] = None,
    assignee_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[TaskResponse]:
    tasks = await task_service.list_tasks(
        current_user=current_user,
        project_id=project_id,
        sprint_id=sprint_id,
        status=status_filter,
        priority=priority,
        assignee_id=assignee_id,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@tasks_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = await task_service.get_task(current_user=current_user, task_id=task_id)
    return TaskResponse.model_validate(task)


@tasks_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = await task_service.update_task(
        current_user=current_user,
        task_id=task_id,
        title=body.title,
        description=body.description,
        task_type=body.task_type,
        status=body.status,
        priority=body.priority,
        story_points=body.story_points,
        sprint_id=body.sprint_id,
        assignee_id=body.assignee_id,
        due_date=body.due_date,
        label_ids=body.label_ids,
    )
    return TaskResponse.model_validate(task)


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> None:
    await task_service.delete_task(current_user=current_user, task_id=task_id)


@tasks_router.post(
    "/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED
)
async def add_comment(
    task_id: uuid.UUID,
    body: TaskCommentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskCommentResponse:
    comment = await task_service.add_comment(
        current_user=current_user, task_id=task_id, content=body.content
    )
    return TaskCommentResponse.model_validate(comment)


@tasks_router.get("/{task_id}/comments", response_model=list[TaskCommentResponse])
async def list_comments(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> list[TaskCommentResponse]:
    comments = await task_service.list_comments(current_user=current_user, task_id=task_id)
    return [TaskCommentResponse.model_validate(c) for c in comments]


@project_labels_router.post("", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    project_id: uuid.UUID,
    body: LabelCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    label_service: Annotated[LabelService, Depends(get_label_service)],
) -> LabelResponse:
    label = await label_service.create_label(
        current_user=current_user, project_id=project_id, name=body.name, color=body.color
    )
    return LabelResponse.model_validate(label)


@project_labels_router.get("", response_model=list[LabelResponse])
async def list_labels(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    label_service: Annotated[LabelService, Depends(get_label_service)],
) -> list[LabelResponse]:
    labels = await label_service.list_labels(current_user=current_user, project_id=project_id)
    return [LabelResponse.model_validate(label) for label in labels]

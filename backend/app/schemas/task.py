"""Task, Label, and TaskComment schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.database.models.enums import TaskPriority, TaskStatus, TaskType


class LabelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6366F1", pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    color: str


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    task_type: TaskType = TaskType.FEATURE
    priority: TaskPriority = TaskPriority.MEDIUM
    story_points: int | None = Field(None, ge=0, le=100)
    sprint_id: uuid.UUID | None = None
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    label_ids: list[uuid.UUID] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    task_type: TaskType | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    story_points: int | None = Field(None, ge=0, le=100)
    sprint_id: uuid.UUID | None = None
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    label_ids: list[uuid.UUID] | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    sprint_id: uuid.UUID | None
    title: str
    description: str | None
    task_type: TaskType
    status: TaskStatus
    priority: TaskPriority
    story_points: int | None
    due_date: date | None
    assignee_id: uuid.UUID | None
    reporter_id: uuid.UUID
    labels: list[LabelResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class TaskCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

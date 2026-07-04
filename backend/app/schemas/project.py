"""Project schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.infrastructure.database.models.enums import ProjectRole, ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    key: str = Field(..., min_length=2, max_length=10)
    description: str | None = None
    repository_url: str | None = None

    @field_validator("key")
    @classmethod
    def uppercase_key(cls, value: str) -> str:
        value = value.strip().upper()
        if not value.isalnum():
            raise ValueError("Project key must be alphanumeric (e.g. 'DEV', 'API2')")
        return value


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = None
    status: ProjectStatus | None = None
    repository_url: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    key: str
    description: str | None
    status: ProjectStatus
    repository_url: str | None
    created_at: datetime


class AddProjectMemberRequest(BaseModel):
    email: EmailStr
    role: ProjectRole = ProjectRole.DEVELOPER


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role: ProjectRole
    created_at: datetime

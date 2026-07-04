"""Sprint schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.infrastructure.database.models.enums import SprintStatus


class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_order(self) -> "SprintCreate":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class SprintUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    goal: str | None = None
    status: SprintStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    goal: str | None
    status: SprintStatus
    start_date: date | None
    end_date: date | None
    created_at: datetime

"""Organization schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.infrastructure.database.models.enums import OrganizationRole


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    logo_url: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    logo_url: str | None
    owner_id: uuid.UUID
    created_at: datetime


class AddOrganizationMemberRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role: OrganizationRole
    created_at: datetime

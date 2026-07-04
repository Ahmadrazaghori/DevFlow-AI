"""Organization endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_active_user, get_organization_service
from app.application.services.organization_service import OrganizationService
from app.infrastructure.database.models.user import User
from app.schemas.organization import (
    AddOrganizationMemberRequest,
    OrganizationCreate,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrganizationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    organization = await org_service.create_organization(current_user=current_user, name=body.name)
    return OrganizationResponse.model_validate(organization)


@router.get("", response_model=list[OrganizationResponse])
async def list_my_organizations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> list[OrganizationResponse]:
    organizations = await org_service.list_my_organizations(current_user=current_user)
    return [OrganizationResponse.model_validate(org) for org in organizations]


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    organization = await org_service.get_organization(
        current_user=current_user, organization_id=organization_id
    )
    return OrganizationResponse.model_validate(organization)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: uuid.UUID,
    body: OrganizationUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    organization = await org_service.update_organization(
        current_user=current_user,
        organization_id=organization_id,
        name=body.name,
        logo_url=body.logo_url,
    )
    return OrganizationResponse.model_validate(organization)


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_organization_member(
    organization_id: uuid.UUID,
    body: AddOrganizationMemberRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationMemberResponse:
    member = await org_service.add_member(
        current_user=current_user,
        organization_id=organization_id,
        email=body.email,
        role=body.role,
    )
    return OrganizationMemberResponse.model_validate(member)


@router.get("/{organization_id}/members", response_model=list[OrganizationMemberResponse])
async def list_organization_members(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    org_service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> list[OrganizationMemberResponse]:
    members = await org_service.list_members(
        current_user=current_user, organization_id=organization_id
    )
    return [OrganizationMemberResponse.model_validate(m) for m in members]

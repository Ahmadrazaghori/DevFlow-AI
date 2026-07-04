"""Shared authorization helpers for organization/project RBAC.

Centralizes the "is this user allowed to do this" checks so every
service applies the same rules consistently, rather than each service
re-implementing membership lookups and role comparisons.
"""

import uuid
from collections.abc import Iterable

from app.core.exceptions import AuthorizationError
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.database.models.enums import OrganizationRole, ProjectRole
from app.infrastructure.database.models.organization import OrganizationMember
from app.infrastructure.database.models.project import ProjectMember


async def require_org_membership(
    org_repository: OrganizationRepository, *, organization_id: uuid.UUID, user_id: uuid.UUID
) -> OrganizationMember:
    membership = await org_repository.get_membership(organization_id=organization_id, user_id=user_id)
    if membership is None:
        raise AuthorizationError("You are not a member of this organization")
    return membership


async def require_org_role(
    org_repository: OrganizationRepository,
    *,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    allowed_roles: Iterable[OrganizationRole],
) -> OrganizationMember:
    membership = await require_org_membership(
        org_repository, organization_id=organization_id, user_id=user_id
    )
    if membership.role not in allowed_roles:
        raise AuthorizationError(
            f"This action requires one of these organization roles: "
            f"{', '.join(r.value for r in allowed_roles)}"
        )
    return membership


async def require_project_membership(
    project_repository: ProjectRepository, *, project_id: uuid.UUID, user_id: uuid.UUID
) -> ProjectMember:
    membership = await project_repository.get_membership(project_id=project_id, user_id=user_id)
    if membership is None:
        raise AuthorizationError("You are not a member of this project")
    return membership


async def require_project_role(
    project_repository: ProjectRepository,
    *,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    allowed_roles: Iterable[ProjectRole],
) -> ProjectMember:
    membership = await require_project_membership(
        project_repository, project_id=project_id, user_id=user_id
    )
    if membership.role not in allowed_roles:
        raise AuthorizationError(
            f"This action requires one of these project roles: "
            f"{', '.join(r.value for r in allowed_roles)}"
        )
    return membership

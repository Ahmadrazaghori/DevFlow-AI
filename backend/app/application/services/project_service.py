"""Project application service."""

import uuid

from app.application.services.authorization import (
    require_org_membership,
    require_org_role,
    require_project_membership,
    require_project_role,
)
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.enums import OrganizationRole, ProjectRole, ProjectStatus
from app.infrastructure.database.models.project import Project, ProjectMember
from app.infrastructure.database.models.user import User


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        org_repository: OrganizationRepository,
        user_repository: UserRepository,
    ) -> None:
        self._projects = project_repository
        self._orgs = org_repository
        self._users = user_repository

    async def create_project(
        self,
        *,
        current_user: User,
        organization_id: uuid.UUID,
        name: str,
        key: str,
        description: str | None,
        repository_url: str | None,
    ) -> Project:
        await require_org_role(
            self._orgs,
            organization_id=organization_id,
            user_id=current_user.id,
            allowed_roles=(OrganizationRole.OWNER, OrganizationRole.ADMIN),
        )

        existing = await self._projects.get_by_key(organization_id=organization_id, key=key)
        if existing is not None:
            raise AlreadyExistsError("Project", "key", key)

        project = await self._projects.create(
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
            repository_url=repository_url,
        )
        await self._projects.add_member(
            project_id=project.id, user_id=current_user.id, role=ProjectRole.MANAGER
        )
        return project

    async def get_project(self, *, current_user: User, project_id: uuid.UUID) -> Project:
        await require_project_membership(
            self._projects, project_id=project_id, user_id=current_user.id
        )
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))
        return project

    async def list_projects(
        self, *, current_user: User, organization_id: uuid.UUID
    ) -> list[Project]:
        await require_org_membership(
            self._orgs, organization_id=organization_id, user_id=current_user.id
        )
        return await self._projects.list_for_organization(organization_id)

    async def update_project(
        self,
        *,
        current_user: User,
        project_id: uuid.UUID,
        name: str | None,
        description: str | None,
        status: ProjectStatus | None,
        repository_url: str | None,
    ) -> Project:
        await require_project_role(
            self._projects,
            project_id=project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if repository_url is not None:
            project.repository_url = repository_url
        return await self._projects.update(project)

    async def add_member(
        self,
        *,
        current_user: User,
        project_id: uuid.UUID,
        email: str,
        role: ProjectRole,
    ) -> ProjectMember:
        await require_project_role(
            self._projects,
            project_id=project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )

        target_user = await self._users.get_by_email(email)
        if target_user is None:
            raise NotFoundError("User", email)

        existing = await self._projects.get_membership(
            project_id=project_id, user_id=target_user.id
        )
        if existing is not None:
            raise AlreadyExistsError("Project membership", "user", email)

        return await self._projects.add_member(
            project_id=project_id, user_id=target_user.id, role=role
        )

    async def list_members(
        self, *, current_user: User, project_id: uuid.UUID
    ) -> list[ProjectMember]:
        await require_project_membership(
            self._projects, project_id=project_id, user_id=current_user.id
        )
        return await self._projects.list_members(project_id)

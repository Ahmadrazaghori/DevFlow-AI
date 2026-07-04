"""SQLAlchemy implementation of ProjectRepository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.database.models.enums import ProjectRole
from app.infrastructure.database.models.project import Project, ProjectMember


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        name: str,
        key: str,
        description: str | None,
        repository_url: str | None,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
            repository_url=repository_url,
        )
        self._session.add(project)
        await self._session.flush()
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return await self._session.get(Project, project_id)

    async def get_by_key(self, *, organization_id: uuid.UUID, key: str) -> Project | None:
        result = await self._session.execute(
            select(Project).where(
                Project.organization_id == organization_id, Project.key == key
            )
        )
        return result.scalar_one_or_none()

    async def list_for_organization(self, organization_id: uuid.UUID) -> list[Project]:
        result = await self._session.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, project: Project) -> Project:
        await self._session.flush()
        return project

    async def add_member(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID, role: ProjectRole
    ) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self._session.add(member)
        await self._session.flush()
        return member

    async def get_membership(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectMember | None:
        result = await self._session.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_members(self, project_id: uuid.UUID) -> list[ProjectMember]:
        result = await self._session.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        return list(result.scalars().all())

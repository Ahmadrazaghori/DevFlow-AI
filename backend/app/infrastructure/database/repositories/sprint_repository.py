"""SQLAlchemy implementation of SprintRepository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.sprint_repository import SprintRepository
from app.infrastructure.database.models.sprint import Sprint


class SQLAlchemySprintRepository(SprintRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, project_id: uuid.UUID, **fields) -> Sprint:
        sprint = Sprint(project_id=project_id, **fields)
        self._session.add(sprint)
        await self._session.flush()
        return sprint

    async def get_by_id(self, sprint_id: uuid.UUID) -> Sprint | None:
        return await self._session.get(Sprint, sprint_id)

    async def list_for_project(self, project_id: uuid.UUID) -> list[Sprint]:
        result = await self._session.execute(
            select(Sprint).where(Sprint.project_id == project_id).order_by(Sprint.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, sprint: Sprint) -> Sprint:
        await self._session.flush()
        return sprint

    async def delete(self, sprint: Sprint) -> None:
        await self._session.delete(sprint)
        await self._session.flush()

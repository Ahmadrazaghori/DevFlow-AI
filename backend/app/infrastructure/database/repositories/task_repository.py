"""SQLAlchemy implementation of TaskRepository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories.task_repository import TaskFilters, TaskRepository
from app.infrastructure.database.models.task import Label, Task


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, project_id: uuid.UUID, reporter_id: uuid.UUID, **fields) -> Task:
        task = Task(project_id=project_id, reporter_id=reporter_id, **fields)
        self._session.add(task)
        await self._session.flush()
        return task

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        result = await self._session.execute(
            select(Task).options(selectinload(Task.labels)).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_for_project(self, project_id: uuid.UUID, filters: TaskFilters) -> list[Task]:
        query = select(Task).options(selectinload(Task.labels)).where(Task.project_id == project_id)
        if filters.sprint_id is not None:
            query = query.where(Task.sprint_id == filters.sprint_id)
        if filters.status is not None:
            query = query.where(Task.status == filters.status)
        if filters.priority is not None:
            query = query.where(Task.priority == filters.priority)
        if filters.assignee_id is not None:
            query = query.where(Task.assignee_id == filters.assignee_id)
        query = query.order_by(Task.created_at.desc())

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, task: Task) -> Task:
        await self._session.flush()
        return task

    async def delete(self, task: Task) -> None:
        await self._session.delete(task)
        await self._session.flush()

    async def set_labels(self, task: Task, label_ids: list[uuid.UUID]) -> None:
        if not label_ids:
            task.labels = []
        else:
            result = await self._session.execute(select(Label).where(Label.id.in_(label_ids)))
            task.labels = list(result.scalars().all())
        await self._session.flush()

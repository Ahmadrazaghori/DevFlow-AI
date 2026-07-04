"""SQLAlchemy implementations of LabelRepository and TaskCommentRepository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.label_repository import LabelRepository, TaskCommentRepository
from app.infrastructure.database.models.task import Label, TaskComment


class SQLAlchemyLabelRepository(LabelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, project_id: uuid.UUID, name: str, color: str) -> Label:
        label = Label(project_id=project_id, name=name, color=color)
        self._session.add(label)
        await self._session.flush()
        return label

    async def list_for_project(self, project_id: uuid.UUID) -> list[Label]:
        result = await self._session.execute(select(Label).where(Label.project_id == project_id))
        return list(result.scalars().all())


class SQLAlchemyTaskCommentRepository(TaskCommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, task_id: uuid.UUID, author_id: uuid.UUID, content: str) -> TaskComment:
        comment = TaskComment(task_id=task_id, author_id=author_id, content=content)
        self._session.add(comment)
        await self._session.flush()
        return comment

    async def list_for_task(self, task_id: uuid.UUID) -> list[TaskComment]:
        result = await self._session.execute(
            select(TaskComment)
            .where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at)
        )
        return list(result.scalars().all())

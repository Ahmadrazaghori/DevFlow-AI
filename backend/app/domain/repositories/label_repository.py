"""Abstract Label and TaskComment repository contracts."""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.task import Label, TaskComment


class LabelRepository(ABC):
    @abstractmethod
    async def create(self, *, project_id: uuid.UUID, name: str, color: str) -> Label: ...

    @abstractmethod
    async def list_for_project(self, project_id: uuid.UUID) -> list[Label]: ...


class TaskCommentRepository(ABC):
    @abstractmethod
    async def create(
        self, *, task_id: uuid.UUID, author_id: uuid.UUID, content: str
    ) -> TaskComment: ...

    @abstractmethod
    async def list_for_task(self, task_id: uuid.UUID) -> list[TaskComment]: ...

"""Abstract Task repository contract."""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.enums import TaskPriority, TaskStatus
from app.infrastructure.database.models.task import Task


class TaskFilters:
    def __init__(
        self,
        *,
        sprint_id: uuid.UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: uuid.UUID | None = None,
    ) -> None:
        self.sprint_id = sprint_id
        self.status = status
        self.priority = priority
        self.assignee_id = assignee_id


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, *, project_id: uuid.UUID, reporter_id: uuid.UUID, **fields) -> Task: ...

    @abstractmethod
    async def get_by_id(self, task_id: uuid.UUID) -> Task | None: ...

    @abstractmethod
    async def list_for_project(self, project_id: uuid.UUID, filters: TaskFilters) -> list[Task]: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task: Task) -> None: ...

    @abstractmethod
    async def set_labels(self, task: Task, label_ids: list[uuid.UUID]) -> None: ...

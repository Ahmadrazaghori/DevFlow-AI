"""Abstract Sprint repository contract."""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.sprint import Sprint


class SprintRepository(ABC):
    @abstractmethod
    async def create(self, *, project_id: uuid.UUID, **fields) -> Sprint: ...

    @abstractmethod
    async def get_by_id(self, sprint_id: uuid.UUID) -> Sprint | None: ...

    @abstractmethod
    async def list_for_project(self, project_id: uuid.UUID) -> list[Sprint]: ...

    @abstractmethod
    async def update(self, sprint: Sprint) -> Sprint: ...

    @abstractmethod
    async def delete(self, sprint: Sprint) -> None: ...

"""Abstract Project repository contract."""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.enums import ProjectRole
from app.infrastructure.database.models.project import Project, ProjectMember


class ProjectRepository(ABC):
    @abstractmethod
    async def create(
        self, *, organization_id: uuid.UUID, name: str, key: str, description: str | None,
        repository_url: str | None,
    ) -> Project: ...

    @abstractmethod
    async def get_by_id(self, project_id: uuid.UUID) -> Project | None: ...

    @abstractmethod
    async def get_by_key(self, *, organization_id: uuid.UUID, key: str) -> Project | None: ...

    @abstractmethod
    async def list_for_organization(self, organization_id: uuid.UUID) -> list[Project]: ...

    @abstractmethod
    async def update(self, project: Project) -> Project: ...

    @abstractmethod
    async def add_member(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID, role: ProjectRole
    ) -> ProjectMember: ...

    @abstractmethod
    async def get_membership(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectMember | None: ...

    @abstractmethod
    async def list_members(self, project_id: uuid.UUID) -> list[ProjectMember]: ...

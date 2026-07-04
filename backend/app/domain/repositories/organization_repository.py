"""Abstract Organization repository contract."""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.enums import OrganizationRole
from app.infrastructure.database.models.organization import Organization, OrganizationMember


class OrganizationRepository(ABC):
    @abstractmethod
    async def create(self, *, name: str, slug: str, owner_id: uuid.UUID) -> Organization: ...

    @abstractmethod
    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Organization | None: ...

    @abstractmethod
    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]: ...

    @abstractmethod
    async def update(self, organization: Organization) -> Organization: ...

    @abstractmethod
    async def add_member(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role: OrganizationRole
    ) -> OrganizationMember: ...

    @abstractmethod
    async def get_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember | None: ...

    @abstractmethod
    async def list_members(self, organization_id: uuid.UUID) -> list[OrganizationMember]: ...

"""SQLAlchemy implementation of OrganizationRepository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories.organization_repository import OrganizationRepository
from app.infrastructure.database.models.enums import OrganizationRole
from app.infrastructure.database.models.organization import Organization, OrganizationMember


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, name: str, slug: str, owner_id: uuid.UUID) -> Organization:
        organization = Organization(name=name, slug=slug, owner_id=owner_id)
        self._session.add(organization)
        await self._session.flush()
        return organization

    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        return await self._session.get(Organization, organization_id)

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self._session.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
        result = await self._session.execute(
            select(Organization)
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
            .order_by(Organization.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, organization: Organization) -> Organization:
        await self._session.flush()
        return organization

    async def add_member(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role: OrganizationRole
    ) -> OrganizationMember:
        member = OrganizationMember(organization_id=organization_id, user_id=user_id, role=role)
        self._session.add(member)
        await self._session.flush()
        return member

    async def get_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember | None:
        result = await self._session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_members(self, organization_id: uuid.UUID) -> list[OrganizationMember]:
        result = await self._session.execute(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == organization_id)
        )
        return list(result.scalars().all())

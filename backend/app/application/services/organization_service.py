"""Organization application service."""

import uuid

from app.application.services.authorization import require_org_membership, require_org_role
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.core.slugify import slugify
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.enums import OrganizationRole
from app.infrastructure.database.models.organization import Organization, OrganizationMember
from app.infrastructure.database.models.user import User


class OrganizationService:
    def __init__(
        self, org_repository: OrganizationRepository, user_repository: UserRepository
    ) -> None:
        self._orgs = org_repository
        self._users = user_repository

    async def create_organization(self, *, current_user: User, name: str) -> Organization:
        base_slug = slugify(name)
        slug = base_slug
        suffix = 1
        while await self._orgs.get_by_slug(slug) is not None:
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        organization = await self._orgs.create(name=name, slug=slug, owner_id=current_user.id)
        await self._orgs.add_member(
            organization_id=organization.id, user_id=current_user.id, role=OrganizationRole.OWNER
        )
        return organization

    async def get_organization(self, *, current_user: User, organization_id: uuid.UUID) -> Organization:
        await require_org_membership(
            self._orgs, organization_id=organization_id, user_id=current_user.id
        )
        organization = await self._orgs.get_by_id(organization_id)
        if organization is None:
            raise NotFoundError("Organization", str(organization_id))
        return organization

    async def list_my_organizations(self, *, current_user: User) -> list[Organization]:
        return await self._orgs.list_for_user(current_user.id)

    async def update_organization(
        self,
        *,
        current_user: User,
        organization_id: uuid.UUID,
        name: str | None,
        logo_url: str | None,
    ) -> Organization:
        await require_org_role(
            self._orgs,
            organization_id=organization_id,
            user_id=current_user.id,
            allowed_roles=(OrganizationRole.OWNER, OrganizationRole.ADMIN),
        )
        organization = await self._orgs.get_by_id(organization_id)
        if organization is None:
            raise NotFoundError("Organization", str(organization_id))

        if name is not None:
            organization.name = name
        if logo_url is not None:
            organization.logo_url = logo_url
        return await self._orgs.update(organization)

    async def add_member(
        self,
        *,
        current_user: User,
        organization_id: uuid.UUID,
        email: str,
        role: OrganizationRole,
    ) -> OrganizationMember:
        await require_org_role(
            self._orgs,
            organization_id=organization_id,
            user_id=current_user.id,
            allowed_roles=(OrganizationRole.OWNER, OrganizationRole.ADMIN),
        )

        target_user = await self._users.get_by_email(email)
        if target_user is None:
            raise NotFoundError("User", email)

        existing = await self._orgs.get_membership(
            organization_id=organization_id, user_id=target_user.id
        )
        if existing is not None:
            raise AlreadyExistsError("Organization membership", "user", email)

        return await self._orgs.add_member(
            organization_id=organization_id, user_id=target_user.id, role=role
        )

    async def list_members(
        self, *, current_user: User, organization_id: uuid.UUID
    ) -> list[OrganizationMember]:
        await require_org_membership(
            self._orgs, organization_id=organization_id, user_id=current_user.id
        )
        return await self._orgs.list_members(organization_id)

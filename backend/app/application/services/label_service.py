"""Label application service."""

import uuid

from app.application.services.authorization import require_project_membership, require_project_role
from app.domain.repositories.label_repository import LabelRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.database.models.enums import ProjectRole
from app.infrastructure.database.models.task import Label
from app.infrastructure.database.models.user import User


class LabelService:
    def __init__(
        self, label_repository: LabelRepository, project_repository: ProjectRepository
    ) -> None:
        self._labels = label_repository
        self._projects = project_repository

    async def create_label(
        self, *, current_user: User, project_id: uuid.UUID, name: str, color: str
    ) -> Label:
        await require_project_role(
            self._projects,
            project_id=project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )
        return await self._labels.create(project_id=project_id, name=name, color=color)

    async def list_labels(self, *, current_user: User, project_id: uuid.UUID) -> list[Label]:
        await require_project_membership(
            self._projects, project_id=project_id, user_id=current_user.id
        )
        return await self._labels.list_for_project(project_id)

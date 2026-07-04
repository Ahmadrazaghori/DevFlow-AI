"""Sprint application service."""

import uuid
from datetime import date

from app.application.services.authorization import require_project_membership, require_project_role
from app.core.exceptions import NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.sprint_repository import SprintRepository
from app.infrastructure.database.models.enums import ProjectRole, SprintStatus
from app.infrastructure.database.models.sprint import Sprint
from app.infrastructure.database.models.user import User


class SprintService:
    def __init__(
        self, sprint_repository: SprintRepository, project_repository: ProjectRepository
    ) -> None:
        self._sprints = sprint_repository
        self._projects = project_repository

    async def create_sprint(
        self,
        *,
        current_user: User,
        project_id: uuid.UUID,
        name: str,
        goal: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> Sprint:
        await require_project_role(
            self._projects,
            project_id=project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )
        return await self._sprints.create(
            project_id=project_id, name=name, goal=goal, start_date=start_date, end_date=end_date
        )

    async def get_sprint(self, *, current_user: User, sprint_id: uuid.UUID) -> Sprint:
        sprint = await self._sprints.get_by_id(sprint_id)
        if sprint is None:
            raise NotFoundError("Sprint", str(sprint_id))
        await require_project_membership(
            self._projects, project_id=sprint.project_id, user_id=current_user.id
        )
        return sprint

    async def list_sprints(self, *, current_user: User, project_id: uuid.UUID) -> list[Sprint]:
        await require_project_membership(
            self._projects, project_id=project_id, user_id=current_user.id
        )
        return await self._sprints.list_for_project(project_id)

    async def update_sprint(
        self,
        *,
        current_user: User,
        sprint_id: uuid.UUID,
        name: str | None,
        goal: str | None,
        status: SprintStatus | None,
        start_date: date | None,
        end_date: date | None,
    ) -> Sprint:
        sprint = await self._sprints.get_by_id(sprint_id)
        if sprint is None:
            raise NotFoundError("Sprint", str(sprint_id))
        await require_project_role(
            self._projects,
            project_id=sprint.project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )

        if name is not None:
            sprint.name = name
        if goal is not None:
            sprint.goal = goal
        if status is not None:
            sprint.status = status
        if start_date is not None:
            sprint.start_date = start_date
        if end_date is not None:
            sprint.end_date = end_date
        return await self._sprints.update(sprint)

    async def delete_sprint(self, *, current_user: User, sprint_id: uuid.UUID) -> None:
        sprint = await self._sprints.get_by_id(sprint_id)
        if sprint is None:
            raise NotFoundError("Sprint", str(sprint_id))
        await require_project_role(
            self._projects,
            project_id=sprint.project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )
        await self._sprints.delete(sprint)

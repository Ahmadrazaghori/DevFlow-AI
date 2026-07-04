"""Task application service.

Also handles TaskComment operations since comments are a small
sub-resource of a task with no independent lifecycle of their own.
"""

import uuid
from datetime import date

from app.application.services.authorization import require_project_membership, require_project_role
from app.core.exceptions import NotFoundError
from app.domain.repositories.label_repository import TaskCommentRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskFilters, TaskRepository
from app.infrastructure.database.models.enums import (
    ProjectRole,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from app.infrastructure.database.models.task import Task, TaskComment
from app.infrastructure.database.models.user import User

# Roles allowed to create/edit tasks. Viewers are read-only.
_EDITOR_ROLES = (ProjectRole.MANAGER, ProjectRole.DEVELOPER)


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        comment_repository: TaskCommentRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._tasks = task_repository
        self._comments = comment_repository
        self._projects = project_repository

    async def create_task(
        self,
        *,
        current_user: User,
        project_id: uuid.UUID,
        title: str,
        description: str | None,
        task_type: TaskType,
        priority: TaskPriority,
        story_points: int | None,
        sprint_id: uuid.UUID | None,
        assignee_id: uuid.UUID | None,
        due_date: date | None,
        label_ids: list[uuid.UUID],
    ) -> Task:
        await require_project_role(
            self._projects,
            project_id=project_id,
            user_id=current_user.id,
            allowed_roles=_EDITOR_ROLES,
        )

        task = await self._tasks.create(
            project_id=project_id,
            reporter_id=current_user.id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            story_points=story_points,
            sprint_id=sprint_id,
            assignee_id=assignee_id,
            due_date=due_date,
        )
        if label_ids:
            await self._tasks.set_labels(task, label_ids)
        return task

    async def get_task(self, *, current_user: User, task_id: uuid.UUID) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        await require_project_membership(
            self._projects, project_id=task.project_id, user_id=current_user.id
        )
        return task

    async def list_tasks(
        self,
        *,
        current_user: User,
        project_id: uuid.UUID,
        sprint_id: uuid.UUID | None,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        assignee_id: uuid.UUID | None,
    ) -> list[Task]:
        await require_project_membership(
            self._projects, project_id=project_id, user_id=current_user.id
        )
        filters = TaskFilters(
            sprint_id=sprint_id, status=status, priority=priority, assignee_id=assignee_id
        )
        return await self._tasks.list_for_project(project_id, filters)

    async def update_task(
        self,
        *,
        current_user: User,
        task_id: uuid.UUID,
        title: str | None,
        description: str | None,
        task_type: TaskType | None,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        story_points: int | None,
        sprint_id: uuid.UUID | None,
        assignee_id: uuid.UUID | None,
        due_date: date | None,
        label_ids: list[uuid.UUID] | None,
    ) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        await require_project_role(
            self._projects,
            project_id=task.project_id,
            user_id=current_user.id,
            allowed_roles=_EDITOR_ROLES,
        )

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if task_type is not None:
            task.task_type = task_type
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if story_points is not None:
            task.story_points = story_points
        if sprint_id is not None:
            task.sprint_id = sprint_id
        if assignee_id is not None:
            task.assignee_id = assignee_id
        if due_date is not None:
            task.due_date = due_date

        task = await self._tasks.update(task)
        if label_ids is not None:
            await self._tasks.set_labels(task, label_ids)
        return task

    async def delete_task(self, *, current_user: User, task_id: uuid.UUID) -> None:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        await require_project_role(
            self._projects,
            project_id=task.project_id,
            user_id=current_user.id,
            allowed_roles=(ProjectRole.MANAGER,),
        )
        await self._tasks.delete(task)

    async def add_comment(
        self, *, current_user: User, task_id: uuid.UUID, content: str
    ) -> TaskComment:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        await require_project_membership(
            self._projects, project_id=task.project_id, user_id=current_user.id
        )
        return await self._comments.create(
            task_id=task_id, author_id=current_user.id, content=content
        )

    async def list_comments(
        self, *, current_user: User, task_id: uuid.UUID
    ) -> list[TaskComment]:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        await require_project_membership(
            self._projects, project_id=task.project_id, user_id=current_user.id
        )
        return await self._comments.list_for_task(task_id)

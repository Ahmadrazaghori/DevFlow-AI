"""Import every ORM model here so they register on Base.metadata.

Alembic's autogenerate (and any code calling Base.metadata.create_all)
relies on this module having imported all model classes first.
"""

from app.infrastructure.database.models.activity_log import ActivityLog
from app.infrastructure.database.models.ai_analysis import AIAnalysis
from app.infrastructure.database.models.auth import RefreshToken
from app.infrastructure.database.models.document import Document
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.database.models.organization import Organization, OrganizationMember
from app.infrastructure.database.models.project import Project, ProjectMember
from app.infrastructure.database.models.sprint import Sprint
from app.infrastructure.database.models.task import Label, Task, TaskComment, task_labels
from app.infrastructure.database.models.user import User

__all__ = [
    "ActivityLog",
    "AIAnalysis",
    "RefreshToken",
    "Document",
    "Notification",
    "Organization",
    "OrganizationMember",
    "Project",
    "ProjectMember",
    "Sprint",
    "Label",
    "Task",
    "TaskComment",
    "task_labels",
    "User",
]

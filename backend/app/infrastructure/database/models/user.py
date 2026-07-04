"""User model.

Represents an individual account. Organization/project-level roles are
stored separately (in OrganizationMember / ProjectMember) since a user
can hold different roles across different organizations and projects —
role is NOT a property of the user themselves.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.activity_log import ActivityLog
    from app.infrastructure.database.models.ai_analysis import AIAnalysis
    from app.infrastructure.database.models.auth import RefreshToken
    from app.infrastructure.database.models.notification import Notification
    from app.infrastructure.database.models.organization import Organization, OrganizationMember
    from app.infrastructure.database.models.project import Project, ProjectMember
    from app.infrastructure.database.models.task import Task, TaskComment


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    owned_organizations: Mapped[list["Organization"]] = relationship(
        back_populates="owner", foreign_keys="Organization.owner_id"
    )
    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    project_memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    reported_tasks: Mapped[list["Task"]] = relationship(
        back_populates="reporter", foreign_keys="Task.reporter_id"
    )
    task_comments: Mapped[list["TaskComment"]] = relationship(back_populates="author")
    ai_analyses_requested: Mapped[list["AIAnalysis"]] = relationship(back_populates="requested_by")
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

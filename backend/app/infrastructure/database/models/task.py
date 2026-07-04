"""Task models.

Task is the core work-item entity. Labels are project-scoped tags
(many-to-many via task_labels). TaskComment threads discussion on a
task. Story points use a small integer (Fibonacci-style values are
enforced at the schema/validation layer, not the DB).
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Integer, String, Table, Text
from sqlalchemy import Column as SAColumn
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.enums import TaskPriority, TaskStatus, TaskType
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.ai_analysis import AIAnalysis
    from app.infrastructure.database.models.project import Project
    from app.infrastructure.database.models.sprint import Sprint
    from app.infrastructure.database.models.user import User


# Many-to-many association: a task can have multiple labels, a label
# can be applied to multiple tasks. Plain Table (not a mapped class)
# since it carries no extra data beyond the two foreign keys.
task_labels = Table(
    "task_labels",
    Base.metadata,
    SAColumn(
        "task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    SAColumn(
        "label_id",
        UUID(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Label(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "labels"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366F1", nullable=False)  # hex color

    # --- Relationships ---
    project: Mapped["Project"] = relationship(back_populates="labels")
    tasks: Mapped[list["Task"]] = relationship(secondary=task_labels, back_populates="labels")

    def __repr__(self) -> str:
        return f"<Label id={self.id} name={self.name}>"


class Task(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    sprint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sprints.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(
        SAEnum(TaskType, name="task_type"), default=TaskType.FEATURE, nullable=False
    )
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="task_status"), default=TaskStatus.BACKLOG, nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, name="task_priority"), default=TaskPriority.MEDIUM, nullable=False
    )
    story_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # --- Relationships ---
    project: Mapped["Project"] = relationship(back_populates="tasks")
    sprint: Mapped["Sprint | None"] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship(
        back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    reporter: Mapped["User"] = relationship(
        back_populates="reported_tasks", foreign_keys=[reporter_id]
    )
    labels: Mapped[list["Label"]] = relationship(secondary=task_labels, back_populates="tasks")
    comments: Mapped[list["TaskComment"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", order_by="TaskComment.created_at"
    )
    ai_analyses: Mapped[list["AIAnalysis"]] = relationship(back_populates="task")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"


class TaskComment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "task_comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Relationships ---
    task: Mapped["Task"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="task_comments")

    def __repr__(self) -> str:
        return f"<TaskComment id={self.id} task={self.task_id}>"

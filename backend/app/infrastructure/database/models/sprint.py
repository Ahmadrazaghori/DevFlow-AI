"""Sprint model.

Represents an Agile sprint/iteration within a Project. Tasks reference
a sprint optionally (backlog tasks have sprint_id = NULL).
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.enums import SprintStatus
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.project import Project
    from app.infrastructure.database.models.task import Task


class Sprint(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sprints"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SprintStatus] = mapped_column(
        SAEnum(SprintStatus, name="sprint_status"),
        default=SprintStatus.PLANNED,
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # --- Relationships ---
    project: Mapped["Project"] = relationship(back_populates="sprints")
    tasks: Mapped[list["Task"]] = relationship(back_populates="sprint")

    def __repr__(self) -> str:
        return f"<Sprint id={self.id} name={self.name} status={self.status}>"

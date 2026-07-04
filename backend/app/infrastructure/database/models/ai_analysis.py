"""AIAnalysis model.

Tracks every AI feature invocation as an async job. A Celery task
processes the request (calling the Anthropic API) and writes the
result back to this row, so the frontend can poll status or receive
it via the notification system. input_data / output_data are JSONB
since each analysis type has a different shape.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.enums import AIAnalysisStatus, AIAnalysisType
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.document import Document
    from app.infrastructure.database.models.project import Project
    from app.infrastructure.database.models.task import Task
    from app.infrastructure.database.models.user import User


class AIAnalysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_analyses"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    analysis_type: Mapped[AIAnalysisType] = mapped_column(
        SAEnum(AIAnalysisType, name="ai_analysis_type"), nullable=False
    )
    status: Mapped[AIAnalysisStatus] = mapped_column(
        SAEnum(AIAnalysisStatus, name="ai_analysis_status"),
        default=AIAnalysisStatus.PENDING,
        nullable=False,
    )

    input_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # --- Relationships ---
    project: Mapped["Project"] = relationship(back_populates="ai_analyses")
    task: Mapped["Task | None"] = relationship(back_populates="ai_analyses")
    requested_by: Mapped["User"] = relationship(back_populates="ai_analyses_requested")
    documents: Mapped[list["Document"]] = relationship(back_populates="ai_analysis")

    def __repr__(self) -> str:
        return f"<AIAnalysis id={self.id} type={self.analysis_type} status={self.status}>"

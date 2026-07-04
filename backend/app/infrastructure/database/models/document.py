"""Document model.

Stores AI-generated documentation artifacts (README, API docs,
architecture diagrams-as-text, deployment guides). Versioned so
regenerating a doc doesn't destroy history.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.enums import DocumentType
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.ai_analysis import AIAnalysis
    from app.infrastructure.database.models.project import Project
    from app.infrastructure.database.models.user import User


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    ai_analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_analyses.id", ondelete="SET NULL"), nullable=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    doc_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # --- Relationships ---
    project: Mapped["Project"] = relationship(back_populates="documents")
    ai_analysis: Mapped["AIAnalysis | None"] = relationship(back_populates="documents")
    created_by: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title!r} v{self.version}>"

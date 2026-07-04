"""ActivityLog model.

Append-only audit trail: "who did what, when, to which entity."
Used for the project activity feed shown in the dashboard, and
doubles as a compliance/audit record. `metadata_` avoids colliding
with SQLAlchemy's reserved `metadata` attribute name.
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.mixins import TimestampMixin, UUIDMixin
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.organization import Organization
    from app.infrastructure.database.models.user import User


class ActivityLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "activity_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "task.created"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "task"
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # --- Relationships ---
    organization: Mapped["Organization"] = relationship(back_populates="activity_logs")
    user: Mapped["User | None"] = relationship(back_populates="activity_logs")

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action}>"

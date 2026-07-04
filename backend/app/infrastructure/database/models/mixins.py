"""Shared SQLAlchemy mixins.

UUIDMixin: every table uses a UUID primary key instead of sequential
integers — standard practice for multi-tenant SaaS (avoids leaking
row counts / enumeration attacks, and merges cleanly across environments).

TimestampMixin: created_at / updated_at columns, server-side defaults
so timestamps are always accurate even for direct DB writes.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

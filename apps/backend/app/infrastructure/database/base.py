"""Declarative base and shared model mixins."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class UUIDPrimaryKeyMixin:
    # `Uuid` (SQLAlchemy 2.0+) compiles to native UUID on Postgres and a
    # portable CHAR(32) on SQLite, so the same models work against a real
    # Postgres in prod/dev and an in-memory SQLite DB in fast unit tests.
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

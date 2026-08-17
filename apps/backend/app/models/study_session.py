"""Study session log.

The data source behind the dashboard's streak and weekly-hours stats. The
Learning Engine writes richer session records here as it grows (skills
practiced, lesson ids, mastery deltas).
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class StudySession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Explicitly timezone-aware: values are always written as `datetime.now(UTC)`,
    # and Postgres silently creates a naive TIMESTAMP column without this, which
    # then fails comparisons against timezone-aware query parameters at runtime.
    studied_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="study_sessions")

    def __repr__(self) -> str:
        return f"<StudySession user_id={self.user_id} minutes={self.duration_minutes}>"

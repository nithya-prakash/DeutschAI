"""A user's vocabulary notebook entry, with SM-2 spaced-repetition state
inlined on the row (ease factor, interval, repetitions, next due date) —
see `app/services/spaced_repetition.py` for the scheduling algorithm itself.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

DEFAULT_EASE_FACTOR = 2.5


class VocabularyItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "vocabulary_items"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    german: Mapped[str] = mapped_column(String(255), nullable=False)
    english: Mapped[str] = mapped_column(String(255), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(String(500), nullable=True)

    ease_factor: Mapped[float] = mapped_column(Float, default=DEFAULT_EASE_FACTOR, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<VocabularyItem {self.german!r} due={self.next_review_date}>"

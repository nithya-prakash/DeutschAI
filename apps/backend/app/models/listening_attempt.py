"""A user's answer to a listening comprehension question, graded
deterministically — structural mirror of ReadingAttempt/QuizAttempt."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.listening_script import ListeningScript


class ListeningAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "listening_attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("listening_scripts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    script: Mapped["ListeningScript"] = relationship()

    def __repr__(self) -> str:
        return f"<ListeningAttempt user_id={self.user_id} correct={self.is_correct}>"

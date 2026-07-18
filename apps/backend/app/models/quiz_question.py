"""Static quiz question bank — global reference data (like GrammarTopic),
seeded via migration. Multiple-choice so grading is fully deterministic and
needs no LLM call.
"""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.grammar_topic import GrammarTopic

# JSONB on Postgres, plain JSON (TEXT-backed) on SQLite — same portability
# trick as the Uuid/Enum types elsewhere in this codebase.
JSONType = JSON().with_variant(JSONB(), "postgresql")


class QuizQuestion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "quiz_questions"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("grammar_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSONType, nullable=False)
    correct_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped["GrammarTopic"] = relationship()

    def __repr__(self) -> str:
        return f"<QuizQuestion topic_id={self.topic_id}>"

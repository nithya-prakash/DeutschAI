"""Static reading comprehension bank — global reference data (like
GrammarTopic/QuizQuestion), seeded via migration. One passage holds its own
single question, mirroring how QuizQuestion inlines question/options rather
than a separate question table (not justified for one question per passage).
Grading is deterministic, same as quizzes — no LLM involved.
"""
from sqlalchemy import Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin
from app.models.user import CEFRLevel

# JSONB on Postgres, plain JSON (TEXT-backed) on SQLite — same portability
# trick as quiz_question.py.
JSONType = JSON().with_variant(JSONB(), "postgresql")


class ReadingPassage(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "reading_passages"

    cefr_level: Mapped[CEFRLevel] = mapped_column(
        Enum(CEFRLevel, name="cefr_level"), nullable=False, index=True
    )
    passage_text: Mapped[str] = mapped_column(Text, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSONType, nullable=False)
    correct_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<ReadingPassage cefr_level={self.cefr_level}>"

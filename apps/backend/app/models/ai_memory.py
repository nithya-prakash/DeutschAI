"""Memory Agent storage: durable notes about a learner's mistakes and gaps,
written by the Assessment Agent (wrong quiz answers) today, and available for
the Tutor Agent or a future recommendation engine to read back.
"""
import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.grammar_topic import GrammarTopic


class MemoryType(StrEnum):
    MISTAKE = "mistake"
    FORGOTTEN_WORD = "forgotten_word"
    PRONUNCIATION_ISSUE = "pronunciation_issue"
    NOTE = "note"


class AIMemory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("grammar_topics.id", ondelete="SET NULL"), nullable=True
    )

    related_topic: Mapped["GrammarTopic | None"] = relationship()

    def __repr__(self) -> str:
        return f"<AIMemory user_id={self.user_id} type={self.memory_type}>"

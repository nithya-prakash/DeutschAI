"""A persisted Conversation Mode speech practice thread and its
turns — audio in, audio out, plus grammar/vocabulary scoring on the
user's turns. Separate from `Conversation`/`ConversationMessage` (the Tutor
Agent's text Q&A threads): different content shape (audio blobs, scores)
and a different agent (`app/ai/conversation_agent.py`)."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.conversation import MessageRole

if TYPE_CHECKING:
    pass


class SpeechConversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "speech_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    turns: Mapped[list["SpeechTurn"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="SpeechTurn.created_at",
    )

    def __repr__(self) -> str:
        return f"<SpeechConversation id={self.id} user_id={self.user_id}>"


class SpeechTurn(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "speech_turns"

    speech_conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("speech_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_object_key: Mapped[str] = mapped_column(Text, nullable=False)

    # Only ever set on USER turns (grading what the learner said); left null
    # for ASSISTANT turns and for USER turns where the Conversation Agent's
    # JSON response failed to parse.
    grammar_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vocabulary_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped["SpeechConversation"] = relationship(back_populates="turns")

    def __repr__(self) -> str:
        return f"<SpeechTurn role={self.role}>"

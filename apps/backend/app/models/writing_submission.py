"""A user's submitted response to a writing prompt, graded by the Writing
Agent (app/ai/writing_agent.py) — a Claude call, same LLM-graded pattern as
Conversation Mode's per-turn grammar/vocabulary scoring. Scores/feedback are
nullable: the row is created before grading so the submitted text is durable
even if grading itself fails (e.g. ANTHROPIC_API_KEY unset)."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.writing_prompt import WritingPrompt


class WritingSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "writing_submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("writing_prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_text: Mapped[str] = mapped_column(Text, nullable=False)
    grammar_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vocabulary_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    task_completion_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    prompt: Mapped["WritingPrompt"] = relationship()

    def __repr__(self) -> str:
        return f"<WritingSubmission user_id={self.user_id}>"

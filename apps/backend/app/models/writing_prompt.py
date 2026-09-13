"""Static writing prompt bank — global reference data, seeded via migration.
Unlike quiz/reading/listening, grading a submission against a prompt isn't
deterministic — see app/ai/writing_agent.py for the LLM-graded flow."""
from sqlalchemy import Enum, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin
from app.models.user import CEFRLevel


class WritingPrompt(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "writing_prompts"

    cefr_level: Mapped[CEFRLevel] = mapped_column(
        Enum(CEFRLevel, name="cefr_level"), nullable=False, index=True
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<WritingPrompt cefr_level={self.cefr_level}>"

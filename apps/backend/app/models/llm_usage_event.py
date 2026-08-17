"""Per-call Claude token usage — backs the admin panel's "LLM token
spend" view. Written by the service layer (TutorService, SpeechService)
after each LLM call, from `response.usage_metadata`."""
import uuid

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LLMUsageEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "llm_usage_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<LLMUsageEvent agent={self.agent_name} "
            f"in={self.input_tokens} out={self.output_tokens}>"
        )

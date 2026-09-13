"""Static listening comprehension bank — same shape as ReadingPassage, but
the content is audio (locally synthesized via Piper, see app/ai/speech/tts.py)
instead of text. `script_text` is the German text that gets synthesized and
is never sent to the frontend — revealing it would let a learner read instead
of listen. `audio_object_key` is nullable and filled in on first synthesis
(see scripts/synthesize_listening_audio.py and ListeningService.get_audio).
"""
from sqlalchemy import Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin
from app.models.user import CEFRLevel

JSONType = JSON().with_variant(JSONB(), "postgresql")


class ListeningScript(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "listening_scripts"

    cefr_level: Mapped[CEFRLevel] = mapped_column(
        Enum(CEFRLevel, name="cefr_level"), nullable=False, index=True
    )
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_object_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSONType, nullable=False)
    correct_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<ListeningScript cefr_level={self.cefr_level}>"

"""Listening comprehension schemas."""
import uuid

from pydantic import BaseModel, Field

from app.models.user import CEFRLevel


class ListeningScriptRead(BaseModel):
    """Deliberately omits `script_text` (would let the learner read instead
    of listen) and the internal `audio_object_key` — playback goes through
    the dedicated audio endpoint only."""

    id: uuid.UUID
    cefr_level: CEFRLevel
    question: str
    options: list[str]


class ListeningAttemptCreate(BaseModel):
    script_id: uuid.UUID
    selected_option_index: int = Field(ge=0)


class ListeningAttemptResult(BaseModel):
    is_correct: bool
    correct_option_index: int
    explanation: str

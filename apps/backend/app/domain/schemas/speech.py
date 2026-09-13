"""Conversation Mode request/response schemas.

Grammar/vocabulary scores are Claude-scored via the Conversation Agent.
Pronunciation/fluency are derived from the STT wrapper's own decode signal
instead (app/ai/speech/stt.py) — heuristic proxies, not a certified
assessment, but real computed signal rather than a placeholder number."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.conversation import MessageRole


class SpeechTurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    text: str
    grammar_score: int | None
    vocabulary_score: int | None
    feedback: str | None
    pronunciation_score: int | None
    fluency_score: int | None
    created_at: datetime


class SpeechConversationSummary(BaseModel):
    id: uuid.UUID
    created_at: datetime
    turn_count: int
    last_turn_preview: str | None


class SpeechConversationRead(BaseModel):
    id: uuid.UUID
    created_at: datetime
    turns: list[SpeechTurnRead]


class SubmitTurnResponse(BaseModel):
    conversation_id: uuid.UUID
    user_turn: SpeechTurnRead
    assistant_turn: SpeechTurnRead

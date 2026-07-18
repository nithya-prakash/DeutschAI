"""Tutor Agent request/response schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.conversation import MessageRole


class AskTutorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    conversation_id: uuid.UUID | None = None


class TutorAnswer(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    sources: list[str]


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    id: uuid.UUID
    created_at: datetime
    message_count: int
    last_message_preview: str | None


class ConversationRead(BaseModel):
    id: uuid.UUID
    created_at: datetime
    messages: list[MessageRead]

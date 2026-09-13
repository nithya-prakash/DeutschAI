"""Reading comprehension schemas."""
import uuid

from pydantic import BaseModel, Field

from app.models.user import CEFRLevel


class ReadingPassageRead(BaseModel):
    """The correct answer is deliberately omitted until an attempt is submitted."""

    id: uuid.UUID
    cefr_level: CEFRLevel
    passage_text: str
    question: str
    options: list[str]


class ReadingAttemptCreate(BaseModel):
    passage_id: uuid.UUID
    selected_option_index: int = Field(ge=0)


class ReadingAttemptResult(BaseModel):
    is_correct: bool
    correct_option_index: int
    explanation: str

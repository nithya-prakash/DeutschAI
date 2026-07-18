"""Quiz / Assessment Agent schemas."""
import uuid

from pydantic import BaseModel, Field


class QuizQuestionRead(BaseModel):
    """The correct answer is deliberately omitted until an attempt is submitted."""

    id: uuid.UUID
    topic_id: uuid.UUID
    topic_name: str
    question: str
    options: list[str]


class QuizAttemptCreate(BaseModel):
    question_id: uuid.UUID
    selected_option_index: int = Field(ge=0)


class QuizAttemptResult(BaseModel):
    is_correct: bool
    correct_option_index: int
    explanation: str

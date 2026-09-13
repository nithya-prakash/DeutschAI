"""Writing exercise schemas."""
import uuid

from pydantic import BaseModel, Field

from app.models.user import CEFRLevel


class WritingPromptRead(BaseModel):
    id: uuid.UUID
    cefr_level: CEFRLevel
    prompt_text: str


class WritingSubmissionCreate(BaseModel):
    prompt_id: uuid.UUID
    submitted_text: str = Field(min_length=1)


class WritingSubmissionResult(BaseModel):
    """Scores/feedback are `None` if the Writing Agent's response couldn't be
    parsed — never a fabricated number (see writing_agent.py)."""

    id: uuid.UUID
    grammar_score: int | None
    vocabulary_score: int | None
    task_completion_score: int | None
    feedback: str | None

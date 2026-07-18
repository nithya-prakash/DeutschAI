"""Vocabulary notebook schemas."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.spaced_repetition import ReviewQuality


class VocabularyItemCreate(BaseModel):
    german: str = Field(min_length=1, max_length=255)
    english: str = Field(min_length=1, max_length=255)
    example_sentence: str | None = Field(default=None, max_length=500)


class VocabularyReviewRequest(BaseModel):
    quality: ReviewQuality


class VocabularyItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    german: str
    english: str
    example_sentence: str | None
    repetitions: int
    next_review_date: date
    last_reviewed_at: datetime | None
    is_due: bool = False

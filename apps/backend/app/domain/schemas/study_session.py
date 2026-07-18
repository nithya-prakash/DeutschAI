"""Schemas for logging and reading study sessions."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudySessionCreate(BaseModel):
    duration_minutes: int = Field(gt=0, le=600)
    note: str | None = Field(default=None, max_length=500)


class StudySessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    studied_on: datetime
    duration_minutes: int
    note: str | None

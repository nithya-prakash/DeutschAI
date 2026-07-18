"""Pydantic schemas for the User resource.

Naming convention: `*Create` for inbound creation payloads, `*Update` for
partial updates, `*Read` for API responses. ORM objects never leave the
service layer directly — they're always mapped to a `*Read` schema first.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import CEFRLevel


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    target_language: str = Field(default="de", max_length=10)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    cefr_level: CEFRLevel | None = None
    target_language: str | None = Field(default=None, max_length=10)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    native_language: str
    target_language: str
    cefr_level: CEFRLevel
    is_active: bool
    is_superuser: bool
    created_at: datetime

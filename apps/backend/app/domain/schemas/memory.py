"""Memory Agent schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.ai_memory import MemoryType


class MemoryRead(BaseModel):
    id: uuid.UUID
    memory_type: MemoryType
    content: str
    related_topic_name: str | None
    created_at: datetime

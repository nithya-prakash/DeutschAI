"""Curriculum topic schemas."""
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.grammar_topic import TopicCategory
from app.models.user_topic_progress import TopicStatus


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: TopicCategory
    name: str
    order_index: int
    status: TopicStatus = TopicStatus.NOT_STARTED


class TopicProgressUpdate(BaseModel):
    status: TopicStatus

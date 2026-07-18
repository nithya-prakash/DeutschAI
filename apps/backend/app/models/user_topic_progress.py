"""Per-user progress against a curriculum topic.

A missing row means "not started" — rows are only created the first time a
user's status on a topic changes, rather than seeding all topics x all users.
"""
import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.grammar_topic import GrammarTopic


class TopicStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"


class UserTopicProgress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_topic_progress"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("grammar_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[TopicStatus] = mapped_column(
        Enum(TopicStatus, name="topic_status"), default=TopicStatus.NOT_STARTED, nullable=False
    )

    topic: Mapped["GrammarTopic"] = relationship()

    def __repr__(self) -> str:
        return f"<UserTopicProgress user_id={self.user_id} topic_id={self.topic_id} {self.status}>"

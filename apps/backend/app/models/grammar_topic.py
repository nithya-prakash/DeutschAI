"""Curriculum reference data.

`GrammarTopic` rows are global reference data (the same for every learner of
a given `target_language`), seeded via migration — not user-editable. Per-user
progress against a topic lives in `UserTopicProgress`, not here.
"""
from enum import StrEnum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin


class TopicCategory(StrEnum):
    GRAMMAR = "grammar"
    EVERYDAY_TOPIC = "everyday_topic"


class GrammarTopic(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "grammar_topics"

    language: Mapped[str] = mapped_column(String(10), default="de", nullable=False)
    category: Mapped[TopicCategory] = mapped_column(
        Enum(TopicCategory, name="topic_category"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<GrammarTopic {self.category}:{self.name}>"

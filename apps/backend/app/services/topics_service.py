"""Curriculum roadmap business logic: joins the global topic list with a
user's own progress against it."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.topic import TopicRead
from app.models.user_topic_progress import TopicStatus
from app.repositories.grammar_topic_repository import GrammarTopicRepository
from app.repositories.user_topic_progress_repository import UserTopicProgressRepository


class TopicNotFoundError(Exception):
    pass


@dataclass
class TopicsService:
    session: AsyncSession

    async def list_for_user(self, user_id: uuid.UUID) -> list[TopicRead]:
        topics = await GrammarTopicRepository(self.session).list_ordered()
        progress_map = await UserTopicProgressRepository(self.session).map_for_user(user_id)

        return [
            TopicRead(
                id=topic.id,
                category=topic.category,
                name=topic.name,
                order_index=topic.order_index,
                status=progress_map.get(topic.id, TopicStatus.NOT_STARTED),
            )
            for topic in topics
        ]

    async def update_progress(
        self, user_id: uuid.UUID, topic_id: uuid.UUID, status: TopicStatus
    ) -> TopicRead:
        topic_repo = GrammarTopicRepository(self.session)
        topic = await topic_repo.get(topic_id)
        if topic is None:
            raise TopicNotFoundError(str(topic_id))

        await UserTopicProgressRepository(self.session).upsert(user_id, topic_id, status)
        await self.session.commit()

        return TopicRead(
            id=topic.id,
            category=topic.category,
            name=topic.name,
            order_index=topic.order_index,
            status=status,
        )

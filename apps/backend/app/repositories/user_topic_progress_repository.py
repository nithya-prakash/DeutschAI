"""Data access for per-user topic progress."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_topic_progress import TopicStatus, UserTopicProgress
from app.repositories.base import BaseRepository


class UserTopicProgressRepository(BaseRepository[UserTopicProgress]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserTopicProgress)

    async def map_for_user(self, user_id: uuid.UUID) -> dict[uuid.UUID, TopicStatus]:
        result = await self.session.execute(
            select(UserTopicProgress).where(UserTopicProgress.user_id == user_id)
        )
        return {row.topic_id: row.status for row in result.scalars().all()}

    async def list_for_user(self, user_id: uuid.UUID) -> list[UserTopicProgress]:
        """Full rows (status + `updated_at`) rather than just the status
        map — `updated_at` on MASTERED rows is the raw signal behind
        progress forecasting."""
        result = await self.session.execute(
            select(UserTopicProgress).where(UserTopicProgress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_topic(
        self, user_id: uuid.UUID, topic_id: uuid.UUID
    ) -> UserTopicProgress | None:
        result = await self.session.execute(
            select(UserTopicProgress).where(
                UserTopicProgress.user_id == user_id, UserTopicProgress.topic_id == topic_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self, user_id: uuid.UUID, topic_id: uuid.UUID, status: TopicStatus
    ) -> UserTopicProgress:
        existing = await self.get_by_user_and_topic(user_id, topic_id)
        if existing is not None:
            existing.status = status
            await self.session.flush()
            return existing

        row = UserTopicProgress(user_id=user_id, topic_id=topic_id, status=status)
        return await self.create(row)

"""Data access for AIMemory (Memory Agent)."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_memory import AIMemory
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[AIMemory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AIMemory)

    async def list_recent_for_user(self, user_id: uuid.UUID, limit: int = 20) -> list[AIMemory]:
        result = await self.session.execute(
            select(AIMemory)
            .where(AIMemory.user_id == user_id)
            .options(selectinload(AIMemory.related_topic))
            .order_by(AIMemory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_topic_for_user(self, user_id: uuid.UUID) -> dict[uuid.UUID, int]:
        """Mistake counts grouped by topic — the raw signal behind
        weakest/strongest topic ranking. Memories with no topic link
        (`related_topic_id` null) aren't attributable to any topic, so
        they're excluded rather than counted against an arbitrary bucket."""
        result = await self.session.execute(
            select(AIMemory.related_topic_id, func.count())
            .where(AIMemory.user_id == user_id, AIMemory.related_topic_id.is_not(None))
            .group_by(AIMemory.related_topic_id)
        )
        return {topic_id: count for topic_id, count in result.all()}

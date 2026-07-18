"""Data access for AIMemory (Memory Agent)."""
import uuid

from sqlalchemy import select
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

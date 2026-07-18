"""Data access for the global GrammarTopic reference table."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grammar_topic import GrammarTopic
from app.repositories.base import BaseRepository


class GrammarTopicRepository(BaseRepository[GrammarTopic]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GrammarTopic)

    async def list_ordered(self) -> list[GrammarTopic]:
        result = await self.session.execute(
            select(GrammarTopic).order_by(GrammarTopic.category, GrammarTopic.order_index)
        )
        return list(result.scalars().all())

"""Data access for VocabularyItem."""
import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary_item import VocabularyItem
from app.repositories.base import BaseRepository


class VocabularyRepository(BaseRepository[VocabularyItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VocabularyItem)

    async def list_for_user(self, user_id: uuid.UUID) -> list[VocabularyItem]:
        result = await self.session.execute(
            select(VocabularyItem)
            .where(VocabularyItem.user_id == user_id)
            .order_by(VocabularyItem.next_review_date.asc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, item_id: uuid.UUID, user_id: uuid.UUID) -> VocabularyItem | None:
        result = await self.session.execute(
            select(VocabularyItem).where(
                VocabularyItem.id == item_id, VocabularyItem.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, item: VocabularyItem) -> None:
        await self.session.delete(item)

    async def count_due(self, user_id: uuid.UUID, today: date) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(VocabularyItem)
            .where(VocabularyItem.user_id == user_id, VocabularyItem.next_review_date <= today)
        )
        return result.scalar_one()

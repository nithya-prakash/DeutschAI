"""Data access for the reading comprehension bank and reading attempts."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reading_attempt import ReadingAttempt
from app.models.reading_passage import ReadingPassage
from app.models.user import CEFRLevel
from app.repositories.base import BaseRepository


class ReadingPassageRepository(BaseRepository[ReadingPassage]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReadingPassage)

    async def random_for_level(self, cefr_level: CEFRLevel) -> ReadingPassage | None:
        result = await self.session.execute(
            select(ReadingPassage)
            .where(ReadingPassage.cefr_level == cefr_level)
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def random_any(self) -> ReadingPassage | None:
        result = await self.session.execute(
            select(ReadingPassage).order_by(func.random()).limit(1)
        )
        return result.scalar_one_or_none()


class ReadingAttemptRepository(BaseRepository[ReadingAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReadingAttempt)

    async def list_is_correct_for_user(self, user_id: uuid.UUID) -> list[bool]:
        result = await self.session.execute(
            select(ReadingAttempt.is_correct).where(ReadingAttempt.user_id == user_id)
        )
        return list(result.scalars().all())

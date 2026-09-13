"""Data access for the listening comprehension bank and listening attempts."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listening_attempt import ListeningAttempt
from app.models.listening_script import ListeningScript
from app.models.user import CEFRLevel
from app.repositories.base import BaseRepository


class ListeningScriptRepository(BaseRepository[ListeningScript]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ListeningScript)

    async def random_for_level(self, cefr_level: CEFRLevel) -> ListeningScript | None:
        result = await self.session.execute(
            select(ListeningScript)
            .where(ListeningScript.cefr_level == cefr_level)
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def random_any(self) -> ListeningScript | None:
        result = await self.session.execute(
            select(ListeningScript).order_by(func.random()).limit(1)
        )
        return result.scalar_one_or_none()


class ListeningAttemptRepository(BaseRepository[ListeningAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ListeningAttempt)

    async def list_is_correct_for_user(self, user_id: uuid.UUID) -> list[bool]:
        result = await self.session.execute(
            select(ListeningAttempt.is_correct).where(ListeningAttempt.user_id == user_id)
        )
        return list(result.scalars().all())

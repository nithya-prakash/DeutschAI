"""Data access for StudySession records."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_session import StudySession
from app.repositories.base import BaseRepository


class StudySessionRepository(BaseRepository[StudySession]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudySession)

    async def list_for_user_since(
        self, user_id: uuid.UUID, since: datetime
    ) -> list[StudySession]:
        result = await self.session.execute(
            select(StudySession)
            .where(StudySession.user_id == user_id, StudySession.studied_on >= since)
            .order_by(StudySession.studied_on.asc())
        )
        return list(result.scalars().all())

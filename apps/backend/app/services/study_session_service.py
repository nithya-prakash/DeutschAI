"""Business logic for logging study sessions."""
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.study_session import StudySessionCreate
from app.models.study_session import StudySession
from app.repositories.study_session_repository import StudySessionRepository


@dataclass
class StudySessionService:
    session: AsyncSession

    async def log_session(self, user_id: uuid.UUID, payload: StudySessionCreate) -> StudySession:
        repo = StudySessionRepository(self.session)
        record = StudySession(
            user_id=user_id,
            studied_on=datetime.now(UTC),
            duration_minutes=payload.duration_minutes,
            note=payload.note,
        )
        record = await repo.create(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

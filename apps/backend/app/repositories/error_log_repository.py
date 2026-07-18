"""Data access for ErrorLogEntry — Phase 6 admin panel's "Error logs" tab."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_log_entry import ErrorLogEntry
from app.repositories.base import BaseRepository


class ErrorLogRepository(BaseRepository[ErrorLogEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ErrorLogEntry)

    async def list_recent(self, limit: int = 50) -> list[ErrorLogEntry]:
        result = await self.session.execute(
            select(ErrorLogEntry).order_by(ErrorLogEntry.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

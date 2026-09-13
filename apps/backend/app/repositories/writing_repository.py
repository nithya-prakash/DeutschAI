"""Data access for the writing prompt bank and writing submissions."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import CEFRLevel
from app.models.writing_prompt import WritingPrompt
from app.models.writing_submission import WritingSubmission
from app.repositories.base import BaseRepository


class WritingPromptRepository(BaseRepository[WritingPrompt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WritingPrompt)

    async def random_for_level(self, cefr_level: CEFRLevel) -> WritingPrompt | None:
        result = await self.session.execute(
            select(WritingPrompt)
            .where(WritingPrompt.cefr_level == cefr_level)
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def random_any(self) -> WritingPrompt | None:
        result = await self.session.execute(
            select(WritingPrompt).order_by(func.random()).limit(1)
        )
        return result.scalar_one_or_none()


class WritingSubmissionRepository(BaseRepository[WritingSubmission]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WritingSubmission)

    async def list_scored_for_user(self, user_id: uuid.UUID) -> list[WritingSubmission]:
        """Every submission the Writing Agent successfully graded — the raw
        signal behind the writing skill score. Submissions where grading
        failed to parse (scores left null, see writing_agent.py) are
        excluded, not zero-filled."""
        result = await self.session.execute(
            select(WritingSubmission).where(
                WritingSubmission.user_id == user_id,
                WritingSubmission.grammar_score.is_not(None),
            )
        )
        return list(result.scalars().all())

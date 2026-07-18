"""Data access for the quiz question bank and quiz attempts."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion
from app.repositories.base import BaseRepository


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, QuizQuestion)

    async def get_with_topic(self, question_id: uuid.UUID) -> QuizQuestion | None:
        result = await self.session.execute(
            select(QuizQuestion)
            .where(QuizQuestion.id == question_id)
            .options(selectinload(QuizQuestion.topic))
        )
        return result.scalar_one_or_none()

    async def random_for_topic(self, topic_id: uuid.UUID) -> QuizQuestion | None:
        result = await self.session.execute(
            select(QuizQuestion)
            .where(QuizQuestion.topic_id == topic_id)
            .options(selectinload(QuizQuestion.topic))
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one_or_none()


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, QuizAttempt)

    async def list_for_user_with_topic(self, user_id: uuid.UUID) -> list[tuple[bool, uuid.UUID]]:
        """(is_correct, topic_id) for every attempt this user has made —
        the raw signal behind grammar skill scoring and weakest/strongest
        topic ranking."""
        result = await self.session.execute(
            select(QuizAttempt.is_correct, QuizQuestion.topic_id)
            .join(QuizQuestion, QuizAttempt.question_id == QuizQuestion.id)
            .where(QuizAttempt.user_id == user_id)
        )
        return [(is_correct, topic_id) for is_correct, topic_id in result.all()]

"""Assessment Agent: deterministic quiz grading, no LLM involved.

Grading a multiple-choice answer is index comparison — there's no ambiguity
to resolve with generation, so this stays rule-based (consistent with "use
traditional logic where appropriate" rather than reaching for an LLM by
default). A wrong answer is recorded as a Memory Agent mistake so it can
inform future study (see app/services/memory_service.py).
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.quiz import QuizAttemptResult, QuizQuestionRead
from app.models.ai_memory import MemoryType
from app.models.quiz_attempt import QuizAttempt
from app.repositories.quiz_repository import QuizAttemptRepository, QuizQuestionRepository
from app.services.memory_service import MemoryService


class QuestionNotFoundError(Exception):
    pass


class NoQuestionsForTopicError(Exception):
    pass


@dataclass
class AssessmentService:
    session: AsyncSession

    async def get_question_for_topic(self, topic_id: uuid.UUID) -> QuizQuestionRead:
        question = await QuizQuestionRepository(self.session).random_for_topic(topic_id)
        if question is None:
            raise NoQuestionsForTopicError(str(topic_id))
        return QuizQuestionRead(
            id=question.id,
            topic_id=question.topic_id,
            topic_name=question.topic.name,
            question=question.question,
            options=question.options,
        )

    async def submit_attempt(
        self, user_id: uuid.UUID, question_id: uuid.UUID, selected_option_index: int
    ) -> QuizAttemptResult:
        question_repo = QuizQuestionRepository(self.session)
        question = await question_repo.get_with_topic(question_id)
        if question is None:
            raise QuestionNotFoundError(str(question_id))

        is_correct = selected_option_index == question.correct_option_index

        attempt = QuizAttempt(
            user_id=user_id,
            question_id=question_id,
            selected_option_index=selected_option_index,
            is_correct=is_correct,
        )
        await QuizAttemptRepository(self.session).create(attempt)

        if not is_correct:
            await MemoryService(self.session).record(
                user_id=user_id,
                memory_type=MemoryType.MISTAKE,
                content=f"Missed a quiz question on {question.topic.name}: \"{question.question}\"",
                related_topic_id=question.topic_id,
            )

        await self.session.commit()

        return QuizAttemptResult(
            is_correct=is_correct,
            correct_option_index=question.correct_option_index,
            explanation=question.explanation,
        )

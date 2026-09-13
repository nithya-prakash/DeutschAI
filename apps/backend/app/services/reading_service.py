"""Reading comprehension service: deterministic grading, no LLM involved —
same rationale as app/services/assessment_service.py. A wrong answer is
recorded as a Memory Agent mistake, same as a wrong quiz answer."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.reading import ReadingAttemptResult, ReadingPassageRead
from app.models.ai_memory import MemoryType
from app.models.reading_attempt import ReadingAttempt
from app.models.user import CEFRLevel
from app.repositories.reading_repository import ReadingAttemptRepository, ReadingPassageRepository
from app.services.memory_service import MemoryService


class PassageNotFoundError(Exception):
    pass


class NoPassagesAvailableError(Exception):
    pass


@dataclass
class ReadingService:
    session: AsyncSession

    async def get_random_passage(self, cefr_level: CEFRLevel) -> ReadingPassageRead:
        repo = ReadingPassageRepository(self.session)
        passage = await repo.random_for_level(cefr_level) or await repo.random_any()
        if passage is None:
            raise NoPassagesAvailableError()
        return ReadingPassageRead(
            id=passage.id,
            cefr_level=passage.cefr_level,
            passage_text=passage.passage_text,
            question=passage.question,
            options=passage.options,
        )

    async def submit_attempt(
        self, user_id: uuid.UUID, passage_id: uuid.UUID, selected_option_index: int
    ) -> ReadingAttemptResult:
        passage = await ReadingPassageRepository(self.session).get(passage_id)
        if passage is None:
            raise PassageNotFoundError(str(passage_id))

        is_correct = selected_option_index == passage.correct_option_index

        attempt = ReadingAttempt(
            user_id=user_id,
            passage_id=passage_id,
            selected_option_index=selected_option_index,
            is_correct=is_correct,
        )
        await ReadingAttemptRepository(self.session).create(attempt)

        if not is_correct:
            await MemoryService(self.session).record(
                user_id=user_id,
                memory_type=MemoryType.MISTAKE,
                content=f'Missed a reading comprehension question: "{passage.question}"',
                related_topic_id=None,
            )

        await self.session.commit()

        return ReadingAttemptResult(
            is_correct=is_correct,
            correct_option_index=passage.correct_option_index,
            explanation=passage.explanation,
        )

"""Writing exercise service: LLM-graded, same pattern as speech_service.py's
Conversation Agent scoring. The submission row is created and flushed before
grading, so the learner's text is durable even if grading itself fails
(e.g. ANTHROPIC_API_KEY unset) — LLMNotConfiguredError propagates uncaught
to the endpoint, same contract as tutor.py/speech.py.

No AIMemory mistake is written here — mirrors Conversation Mode (also
LLM-scored), not Quiz/Reading/Listening (deterministic MCQ grading, where a
wrong answer is an unambiguous "mistake" worth recording)."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.writing_agent import run_writing_grading
from app.core.config import get_settings
from app.domain.schemas.writing import WritingPromptRead, WritingSubmissionResult
from app.models.llm_usage_event import LLMUsageEvent
from app.models.user import CEFRLevel, User
from app.models.writing_submission import WritingSubmission
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.writing_repository import WritingPromptRepository, WritingSubmissionRepository

settings = get_settings()


class PromptNotFoundError(Exception):
    pass


class NoPromptsAvailableError(Exception):
    pass


@dataclass
class WritingService:
    session: AsyncSession

    async def get_random_prompt(self, cefr_level: CEFRLevel) -> WritingPromptRead:
        repo = WritingPromptRepository(self.session)
        prompt = await repo.random_for_level(cefr_level) or await repo.random_any()
        if prompt is None:
            raise NoPromptsAvailableError()
        return WritingPromptRead(
            id=prompt.id, cefr_level=prompt.cefr_level, prompt_text=prompt.prompt_text
        )

    async def submit_writing(
        self, user: User, prompt_id: uuid.UUID, submitted_text: str
    ) -> WritingSubmissionResult:
        prompt = await WritingPromptRepository(self.session).get(prompt_id)
        if prompt is None:
            raise PromptNotFoundError(str(prompt_id))

        submission_repo = WritingSubmissionRepository(self.session)
        submission = await submission_repo.create(
            WritingSubmission(user_id=user.id, prompt_id=prompt_id, submitted_text=submitted_text)
        )

        # Propagates LLMNotConfiguredError to the endpoint if no API key is
        # set — deliberately not caught here, see writing_agent.py.
        result = run_writing_grading(
            prompt_text=prompt.prompt_text,
            submitted_text=submitted_text,
            cefr_level=user.cefr_level.value,
        )

        submission.grammar_score = result["grammar_score"]
        submission.vocabulary_score = result["vocabulary_score"]
        submission.task_completion_score = result["task_completion_score"]
        submission.feedback = result["feedback"]

        await LLMUsageRepository(self.session).create(
            LLMUsageEvent(
                user_id=user.id,
                agent_name="writing",
                model=settings.ANTHROPIC_MODEL,
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
            )
        )

        await self.session.commit()

        return WritingSubmissionResult(
            id=submission.id,
            grammar_score=submission.grammar_score,
            vocabulary_score=submission.vocabulary_score,
            task_completion_score=submission.task_completion_score,
            feedback=submission.feedback,
        )

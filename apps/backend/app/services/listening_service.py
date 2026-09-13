"""Listening comprehension service: deterministic grading (same rationale as
reading/assessment services) plus audio delivery. Scripts are pre-synthesized
by scripts/synthesize_listening_audio.py after a migration seeds them; if a
script's audio hasn't been synthesized yet for any reason, `get_audio`
self-heals by synthesizing it on first request and caching the result, so
the exercise never hard-fails on a missing pre-synthesis step."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.speech.tts import synthesize_speech
from app.domain.schemas.listening import ListeningAttemptResult, ListeningScriptRead
from app.infrastructure.object_store.minio_client import ObjectStore
from app.models.ai_memory import MemoryType
from app.models.listening_attempt import ListeningAttempt
from app.models.user import CEFRLevel
from app.repositories.listening_repository import (
    ListeningAttemptRepository,
    ListeningScriptRepository,
)
from app.services.memory_service import MemoryService


class ScriptNotFoundError(Exception):
    pass


class NoScriptsAvailableError(Exception):
    pass


@dataclass
class ListeningService:
    session: AsyncSession
    object_store: ObjectStore

    async def get_random_script(self, cefr_level: CEFRLevel) -> ListeningScriptRead:
        repo = ListeningScriptRepository(self.session)
        script = await repo.random_for_level(cefr_level) or await repo.random_any()
        if script is None:
            raise NoScriptsAvailableError()
        return ListeningScriptRead(
            id=script.id,
            cefr_level=script.cefr_level,
            question=script.question,
            options=script.options,
        )

    async def get_audio(self, script_id: uuid.UUID) -> tuple[bytes, str]:
        repo = ListeningScriptRepository(self.session)
        script = await repo.get(script_id)
        if script is None:
            raise ScriptNotFoundError(str(script_id))

        if script.audio_object_key is None:
            key = f"listening/{script.id}.wav"
            audio_bytes = synthesize_speech(script.script_text)
            self.object_store.put_object(key, audio_bytes, "audio/wav")
            script.audio_object_key = key
            await self.session.commit()
            return audio_bytes, "audio/wav"

        return self.object_store.get_object(script.audio_object_key), "audio/wav"

    async def submit_attempt(
        self, user_id: uuid.UUID, script_id: uuid.UUID, selected_option_index: int
    ) -> ListeningAttemptResult:
        script = await ListeningScriptRepository(self.session).get(script_id)
        if script is None:
            raise ScriptNotFoundError(str(script_id))

        is_correct = selected_option_index == script.correct_option_index

        attempt = ListeningAttempt(
            user_id=user_id,
            script_id=script_id,
            selected_option_index=selected_option_index,
            is_correct=is_correct,
        )
        await ListeningAttemptRepository(self.session).create(attempt)

        if not is_correct:
            await MemoryService(self.session).record(
                user_id=user_id,
                memory_type=MemoryType.MISTAKE,
                content=f'Missed a listening comprehension question: "{script.question}"',
                related_topic_id=None,
            )

        await self.session.commit()

        return ListeningAttemptResult(
            is_correct=is_correct,
            correct_option_index=script.correct_option_index,
            explanation=script.explanation,
        )

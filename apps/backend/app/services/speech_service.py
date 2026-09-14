"""Conversation Mode business logic: turn persistence + audio storage around
the STT/TTS wrappers (`app/ai/speech/`) and the Conversation Agent graph
(`app/ai/conversation_agent.py`)."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.conversation_agent import run_conversation_turn
from app.ai.speech.stt import transcribe_audio
from app.ai.speech.tts import synthesize_speech
from app.ai.tutor_agent import get_active_model_name
from app.domain.schemas.speech import (
    SpeechConversationRead,
    SpeechConversationSummary,
    SpeechTurnRead,
    SubmitTurnResponse,
)
from app.infrastructure.object_store.minio_client import ObjectStore
from app.models.conversation import MessageRole
from app.models.llm_usage_event import LLMUsageEvent
from app.models.speech_conversation import SpeechConversation
from app.models.user import User
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.speech_conversation_repository import SpeechConversationRepository

# Known browser MediaRecorder mime types <-> a stable file extension, so the
# original content-type survives the round trip through object storage
# without a dedicated DB column.
_EXTENSION_BY_CONTENT_TYPE = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".m4a",
    "audio/wav": ".wav",
    "audio/mpeg": ".mp3",
}
_CONTENT_TYPE_BY_EXTENSION = {v: k for k, v in _EXTENSION_BY_CONTENT_TYPE.items()}
_DEFAULT_EXTENSION = ".bin"


class ConversationNotFoundError(Exception):
    pass


class TurnNotFoundError(Exception):
    pass


class EmptyAudioError(Exception):
    pass


@dataclass
class SpeechService:
    session: AsyncSession
    object_store: ObjectStore

    async def submit_turn(
        self,
        user: User,
        conversation_id: uuid.UUID | None,
        audio_bytes: bytes,
        content_type: str,
    ) -> SubmitTurnResponse:
        if not audio_bytes:
            raise EmptyAudioError("No audio data received")

        repo = SpeechConversationRepository(self.session)

        if conversation_id is not None:
            conversation = await repo.get_for_user(conversation_id, user.id)
            if conversation is None:
                raise ConversationNotFoundError(str(conversation_id))
            # `.turns` is eager-loaded by `get_for_user` (selectinload) — safe to
            # read synchronously. A freshly created conversation below has no
            # turns yet, so there's nothing to eager-load for that branch.
            history = [(turn.role.value, turn.text) for turn in conversation.turns]
        else:
            conversation = await repo.create(SpeechConversation(user_id=user.id))
            await self.session.flush()
            history = []

        transcription = transcribe_audio(audio_bytes)

        user_extension = _EXTENSION_BY_CONTENT_TYPE.get(content_type, _DEFAULT_EXTENSION)
        user_key = f"speech/{conversation.id}/{uuid.uuid4()}{user_extension}"
        self.object_store.put_object(
            user_key, audio_bytes, content_type or "application/octet-stream"
        )
        user_turn = await repo.add_turn(
            conversation.id, MessageRole.USER, transcription.text, user_key
        )
        user_turn.pronunciation_score = transcription.pronunciation_score
        user_turn.fluency_score = transcription.fluency_score

        # Propagates tutor_agent.LLMNotConfiguredError to the endpoint if no
        # API key is set — deliberately not caught here, see conversation_agent.py.
        result = run_conversation_turn(
            transcription.text, cefr_level=user.cefr_level.value, history=history
        )

        user_turn.grammar_score = result["grammar_score"]
        user_turn.vocabulary_score = result["vocabulary_score"]
        user_turn.feedback = result["feedback"]

        await LLMUsageRepository(self.session).create(
            LLMUsageEvent(
                user_id=user.id,
                agent_name="conversation",
                model=get_active_model_name(),
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
            )
        )

        reply_audio = synthesize_speech(result["reply"])
        assistant_key = f"speech/{conversation.id}/{uuid.uuid4()}.wav"
        self.object_store.put_object(assistant_key, reply_audio, "audio/wav")
        assistant_turn = await repo.add_turn(
            conversation.id, MessageRole.ASSISTANT, result["reply"], assistant_key
        )

        await self.session.commit()

        return SubmitTurnResponse(
            conversation_id=conversation.id,
            user_turn=SpeechTurnRead.model_validate(user_turn, from_attributes=True),
            assistant_turn=SpeechTurnRead.model_validate(assistant_turn, from_attributes=True),
        )

    async def list_conversations(self, user_id: uuid.UUID) -> list[SpeechConversationSummary]:
        conversations = await SpeechConversationRepository(self.session).list_for_user(user_id)
        summaries = []
        for conv in conversations:
            last = conv.turns[-1] if conv.turns else None
            preview = None
            if last:
                preview = last.text[:120] + "…" if len(last.text) > 120 else last.text
            summaries.append(
                SpeechConversationSummary(
                    id=conv.id,
                    created_at=conv.created_at,
                    turn_count=len(conv.turns),
                    last_turn_preview=preview,
                )
            )
        return summaries

    async def get_conversation(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> SpeechConversationRead:
        repo = SpeechConversationRepository(self.session)
        conversation = await repo.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise ConversationNotFoundError(str(conversation_id))
        return SpeechConversationRead.model_validate(conversation, from_attributes=True)

    async def get_audio(self, turn_id: uuid.UUID, user_id: uuid.UUID) -> tuple[bytes, str]:
        repo = SpeechConversationRepository(self.session)
        turn = await repo.get_turn_for_user(turn_id, user_id)
        if turn is None:
            raise TurnNotFoundError(str(turn_id))

        extension = next(
            (ext for ext in _CONTENT_TYPE_BY_EXTENSION if turn.audio_object_key.endswith(ext)),
            None,
        )
        content_type = _CONTENT_TYPE_BY_EXTENSION.get(extension, "application/octet-stream")
        return self.object_store.get_object(turn.audio_object_key), content_type

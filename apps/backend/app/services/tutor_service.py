"""Tutor Agent business logic: conversation persistence around the
retrieve->generate graph in app/ai/tutor_agent.py."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tutor_agent import ask_tutor
from app.core.config import get_settings
from app.domain.schemas.tutor import (
    AskTutorRequest,
    ConversationRead,
    ConversationSummary,
    TutorAnswer,
)
from app.models.conversation import Conversation, MessageRole
from app.models.llm_usage_event import LLMUsageEvent
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.llm_usage_repository import LLMUsageRepository

settings = get_settings()


class ConversationNotFoundError(Exception):
    pass


@dataclass
class TutorService:
    session: AsyncSession

    async def ask(self, user: User, payload: AskTutorRequest) -> TutorAnswer:
        repo = ConversationRepository(self.session)

        if payload.conversation_id is not None:
            conversation = await repo.get_for_user(payload.conversation_id, user.id)
            if conversation is None:
                raise ConversationNotFoundError(str(payload.conversation_id))
        else:
            conversation = await repo.create(Conversation(user_id=user.id))
            await self.session.flush()

        await repo.add_message(conversation.id, MessageRole.USER, payload.question)

        # Propagates LLMNotConfiguredError to the endpoint if no API key is set —
        # deliberately not caught here, see app/ai/tutor_agent.py.
        result = ask_tutor(payload.question, cefr_level=user.cefr_level.value)

        await repo.add_message(conversation.id, MessageRole.ASSISTANT, result["answer"])
        await LLMUsageRepository(self.session).create(
            LLMUsageEvent(
                user_id=user.id,
                agent_name="tutor",
                model=settings.ANTHROPIC_MODEL,
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
            )
        )
        await self.session.commit()

        sources = sorted({chunk.topic_name for chunk in result["context_chunks"]})
        return TutorAnswer(
            conversation_id=conversation.id, answer=result["answer"], sources=sources
        )

    async def list_conversations(self, user_id: uuid.UUID) -> list[ConversationSummary]:
        conversations = await ConversationRepository(self.session).list_for_user(user_id)
        summaries = []
        for conv in conversations:
            last = conv.messages[-1] if conv.messages else None
            preview = (last.content[:120] + "…") if last and len(last.content) > 120 else (
                last.content if last else None
            )
            summaries.append(
                ConversationSummary(
                    id=conv.id,
                    created_at=conv.created_at,
                    message_count=len(conv.messages),
                    last_message_preview=preview,
                )
            )
        return summaries

    async def get_conversation(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> ConversationRead:
        conv_repo = ConversationRepository(self.session)
        conversation = await conv_repo.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise ConversationNotFoundError(str(conversation_id))
        return ConversationRead.model_validate(conversation, from_attributes=True)

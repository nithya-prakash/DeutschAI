"""Data access for Conversation Mode speech conversations and their turns."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import MessageRole
from app.models.speech_conversation import SpeechConversation, SpeechTurn
from app.repositories.base import BaseRepository


class SpeechConversationRepository(BaseRepository[SpeechConversation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SpeechConversation)

    async def get_for_user(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> SpeechConversation | None:
        result = await self.session.execute(
            select(SpeechConversation)
            .where(SpeechConversation.id == conversation_id, SpeechConversation.user_id == user_id)
            .options(selectinload(SpeechConversation.turns))
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[SpeechConversation]:
        result = await self.session.execute(
            select(SpeechConversation)
            .where(SpeechConversation.user_id == user_id)
            .options(selectinload(SpeechConversation.turns))
            .order_by(SpeechConversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_turn(
        self,
        conversation_id: uuid.UUID,
        role: MessageRole,
        text: str,
        audio_object_key: str,
    ) -> SpeechTurn:
        turn = SpeechTurn(
            speech_conversation_id=conversation_id,
            role=role,
            text=text,
            audio_object_key=audio_object_key,
        )
        self.session.add(turn)
        await self.session.flush()
        return turn

    async def get_turn_for_user(
        self, turn_id: uuid.UUID, user_id: uuid.UUID
    ) -> SpeechTurn | None:
        result = await self.session.execute(
            select(SpeechTurn)
            .join(SpeechConversation, SpeechTurn.speech_conversation_id == SpeechConversation.id)
            .where(SpeechTurn.id == turn_id, SpeechConversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_scored_user_turns(self, user_id: uuid.UUID) -> list[SpeechTurn]:
        """Every USER turn (across all of this user's conversations) that
        the Conversation Agent scored — the raw signal behind the speaking
        skill score. Assistant turns and unparseable-response turns (scores
        left null, see conversation_agent.py) are excluded, not zero-filled."""
        result = await self.session.execute(
            select(SpeechTurn)
            .join(SpeechConversation, SpeechTurn.speech_conversation_id == SpeechConversation.id)
            .where(
                SpeechConversation.user_id == user_id,
                SpeechTurn.role == MessageRole.USER,
                SpeechTurn.grammar_score.is_not(None),
            )
        )
        return list(result.scalars().all())

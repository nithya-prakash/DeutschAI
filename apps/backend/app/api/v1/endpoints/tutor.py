"""Tutor Agent endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tutor_agent import LLMNotConfiguredError
from app.api.deps import get_current_user
from app.domain.schemas.tutor import (
    AskTutorRequest,
    ConversationRead,
    ConversationSummary,
    TutorAnswer,
)
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.tutor_service import ConversationNotFoundError, TutorService

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.post("/ask", response_model=TutorAnswer)
async def ask_tutor_endpoint(
    payload: AskTutorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TutorAnswer:
    try:
        return await TutorService(db).ask(current_user, payload)
    except ConversationNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        ) from err
    except LLMNotConfiguredError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        ) from err


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationSummary]:
    return await TutorService(db).list_conversations(current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationRead:
    try:
        return await TutorService(db).get_conversation(conversation_id, current_user.id)
    except ConversationNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        ) from err

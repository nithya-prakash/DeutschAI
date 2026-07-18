"""Conversation Mode endpoints — Phase 4 speech practice."""
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tutor_agent import LLMNotConfiguredError
from app.api.deps import get_current_user, get_object_storage
from app.domain.schemas.speech import (
    SpeechConversationRead,
    SpeechConversationSummary,
    SubmitTurnResponse,
)
from app.infrastructure.database.session import get_db
from app.infrastructure.object_store.minio_client import ObjectStore
from app.models.user import User
from app.services.speech_service import (
    ConversationNotFoundError,
    EmptyAudioError,
    SpeechService,
    TurnNotFoundError,
)

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/turns", response_model=SubmitTurnResponse)
async def submit_turn(
    audio: UploadFile = File(...),
    conversation_id: uuid.UUID | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> SubmitTurnResponse:
    audio_bytes = await audio.read()
    try:
        return await SpeechService(db, object_store).submit_turn(
            current_user, conversation_id, audio_bytes, audio.content_type or ""
        )
    except EmptyAudioError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    except ConversationNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        ) from err
    except LLMNotConfiguredError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        ) from err


@router.get("/conversations", response_model=list[SpeechConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> list[SpeechConversationSummary]:
    return await SpeechService(db, object_store).list_conversations(current_user.id)


@router.get("/conversations/{conversation_id}", response_model=SpeechConversationRead)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> SpeechConversationRead:
    try:
        return await SpeechService(db, object_store).get_conversation(
            conversation_id, current_user.id
        )
    except ConversationNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        ) from err


@router.get("/turns/{turn_id}/audio")
async def get_turn_audio(
    turn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> Response:
    try:
        audio_bytes, content_type = await SpeechService(db, object_store).get_audio(
            turn_id, current_user.id
        )
    except TurnNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Turn not found"
        ) from err
    return Response(content=audio_bytes, media_type=content_type)

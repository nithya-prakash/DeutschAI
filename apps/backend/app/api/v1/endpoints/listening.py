"""Listening comprehension endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_object_storage
from app.domain.schemas.listening import (
    ListeningAttemptCreate,
    ListeningAttemptResult,
    ListeningScriptRead,
)
from app.infrastructure.database.session import get_db
from app.infrastructure.object_store.minio_client import ObjectStore
from app.models.user import User
from app.services.listening_service import (
    ListeningService,
    NoScriptsAvailableError,
    ScriptNotFoundError,
)

router = APIRouter(prefix="/listening", tags=["listening"])


@router.get("/scripts/random", response_model=ListeningScriptRead)
async def get_random_script(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> ListeningScriptRead:
    try:
        return await ListeningService(db, object_store).get_random_script(current_user.cefr_level)
    except NoScriptsAvailableError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No listening scripts available"
        ) from err


@router.get("/scripts/{script_id}/audio")
async def get_script_audio(
    script_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> Response:
    try:
        audio_bytes, content_type = await ListeningService(db, object_store).get_audio(script_id)
    except ScriptNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Script not found"
        ) from err
    return Response(content=audio_bytes, media_type=content_type)


@router.post("/attempts", response_model=ListeningAttemptResult)
async def submit_attempt(
    payload: ListeningAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    object_store: ObjectStore = Depends(get_object_storage),
) -> ListeningAttemptResult:
    try:
        return await ListeningService(db, object_store).submit_attempt(
            current_user.id, payload.script_id, payload.selected_option_index
        )
    except ScriptNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Script not found"
        ) from err

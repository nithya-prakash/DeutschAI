"""Reading comprehension endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.reading import (
    ReadingAttemptCreate,
    ReadingAttemptResult,
    ReadingPassageRead,
)
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.reading_service import (
    NoPassagesAvailableError,
    PassageNotFoundError,
    ReadingService,
)

router = APIRouter(prefix="/reading", tags=["reading"])


@router.get("/passages/random", response_model=ReadingPassageRead)
async def get_random_passage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadingPassageRead:
    try:
        return await ReadingService(db).get_random_passage(current_user.cefr_level)
    except NoPassagesAvailableError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No reading passages available"
        ) from err


@router.post("/attempts", response_model=ReadingAttemptResult)
async def submit_attempt(
    payload: ReadingAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadingAttemptResult:
    try:
        return await ReadingService(db).submit_attempt(
            current_user.id, payload.passage_id, payload.selected_option_index
        )
    except PassageNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Passage not found"
        ) from err

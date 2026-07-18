"""Vocabulary notebook endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.vocabulary import (
    VocabularyItemCreate,
    VocabularyItemRead,
    VocabularyReviewRequest,
)
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.vocabulary_service import VocabularyItemNotFoundError, VocabularyService

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("", response_model=list[VocabularyItemRead])
async def list_vocabulary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[VocabularyItemRead]:
    return await VocabularyService(db).list_for_user(current_user.id)


@router.post("", response_model=VocabularyItemRead, status_code=status.HTTP_201_CREATED)
async def add_word(
    payload: VocabularyItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VocabularyItemRead:
    return await VocabularyService(db).add_word(current_user.id, payload)


@router.post("/{item_id}/review", response_model=VocabularyItemRead)
async def review_word(
    item_id: uuid.UUID,
    payload: VocabularyReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VocabularyItemRead:
    try:
        return await VocabularyService(db).review_word(current_user.id, item_id, payload.quality)
    except VocabularyItemNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Word not found"
        ) from err


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await VocabularyService(db).delete_word(current_user.id, item_id)
    except VocabularyItemNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Word not found"
        ) from err

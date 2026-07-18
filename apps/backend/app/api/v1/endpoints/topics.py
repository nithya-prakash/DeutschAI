"""Curriculum roadmap endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.topic import TopicProgressUpdate, TopicRead
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.topics_service import TopicNotFoundError, TopicsService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=list[TopicRead])
async def list_topics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TopicRead]:
    return await TopicsService(db).list_for_user(current_user.id)


@router.patch("/{topic_id}/progress", response_model=TopicRead)
async def update_topic_progress(
    topic_id: uuid.UUID,
    payload: TopicProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TopicRead:
    try:
        return await TopicsService(db).update_progress(current_user.id, topic_id, payload.status)
    except TopicNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
        ) from err

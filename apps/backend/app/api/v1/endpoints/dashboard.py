"""Dashboard summary and study-session logging endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.dashboard import DashboardSummary
from app.domain.schemas.study_session import StudySessionCreate, StudySessionRead
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.services.study_session_service import StudySessionService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    return await DashboardService(db).get_summary(current_user.id)


@router.post(
    "/study-sessions", response_model=StudySessionRead, status_code=status.HTTP_201_CREATED
)
async def log_study_session(
    payload: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudySessionRead:
    record = await StudySessionService(db).log_session(current_user.id, payload)
    return StudySessionRead.model_validate(record)

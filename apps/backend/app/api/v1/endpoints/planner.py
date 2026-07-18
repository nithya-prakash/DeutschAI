"""Daily planner endpoint."""
import redis.asyncio as redis
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.domain.schemas.planner import DailyPlan
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.planner_service import PlannerService

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get("/today", response_model=DailyPlan)
async def get_today_plan(
    available_minutes: int = Query(default=45, ge=5, le=300),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> DailyPlan:
    return await PlannerService(db, redis_client).get_today_plan(current_user.id, available_minutes)

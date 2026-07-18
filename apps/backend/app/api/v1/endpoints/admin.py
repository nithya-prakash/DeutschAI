"""Admin panel endpoints — every route gated on `get_current_superuser`."""
import redis.asyncio as redis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_object_storage, get_redis
from app.domain.schemas.admin import (
    ErrorLogEntryRead,
    LLMUsageSummary,
    SessionActivity,
    SystemHealth,
)
from app.domain.schemas.user import UserRead
from app.infrastructure.database.session import get_db
from app.infrastructure.object_store.minio_client import ObjectStore
from app.models.user import User
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


def _service(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    object_store: ObjectStore = Depends(get_object_storage),
) -> AdminService:
    return AdminService(session=db, redis_client=redis_client, object_store=object_store)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _current_user: User = Depends(get_current_superuser),
    service: AdminService = Depends(_service),
) -> list[UserRead]:
    return await service.list_users()


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    _current_user: User = Depends(get_current_superuser),
    service: AdminService = Depends(_service),
) -> SystemHealth:
    return await service.get_system_health()


@router.get("/llm-usage", response_model=LLMUsageSummary)
async def get_llm_usage(
    _current_user: User = Depends(get_current_superuser),
    service: AdminService = Depends(_service),
) -> LLMUsageSummary:
    return await service.get_llm_usage_summary()


@router.get("/session-activity", response_model=SessionActivity)
async def get_session_activity(
    _current_user: User = Depends(get_current_superuser),
    service: AdminService = Depends(_service),
) -> SessionActivity:
    return await service.get_session_activity()


@router.get("/error-logs", response_model=list[ErrorLogEntryRead])
async def list_error_logs(
    _current_user: User = Depends(get_current_superuser),
    service: AdminService = Depends(_service),
) -> list[ErrorLogEntryRead]:
    return await service.list_error_logs()

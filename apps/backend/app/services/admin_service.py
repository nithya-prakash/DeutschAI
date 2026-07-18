"""Admin panel business logic: system health, LLM usage, session activity,
error logs, and the user list. Every value is either real data already in
the DB, a real reachability check performed at request time, or an honest
zero/empty result — nothing here is fabricated (see docs/ARCHITECTURE.md).
Gated on `get_current_superuser` at the endpoint layer, not here.
"""
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.speech import stt, tts
from app.core.config import get_settings
from app.domain.schemas.admin import (
    AgentUsageTotals,
    ErrorLogEntryRead,
    LLMUsageSummary,
    ServiceStatus,
    SessionActivity,
    SystemHealth,
)
from app.domain.schemas.user import UserRead
from app.infrastructure.object_store.minio_client import ObjectStore
from app.infrastructure.vector_store.qdrant_client import get_qdrant_client
from app.repositories.error_log_repository import ErrorLogRepository
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.study_session_repository import StudySessionRepository
from app.repositories.user_repository import UserRepository

settings = get_settings()


@dataclass
class AdminService:
    session: AsyncSession
    redis_client: redis.Redis
    object_store: ObjectStore

    async def list_users(self) -> list[UserRead]:
        users = await UserRepository(self.session).list_all(limit=1000)
        return [UserRead.model_validate(user) for user in users]

    async def get_system_health(self) -> SystemHealth:
        services = [
            ServiceStatus(name="postgres", reachable=await self._check_postgres()),
            ServiceStatus(name="redis", reachable=await self._check_redis()),
            ServiceStatus(name="qdrant", reachable=self._check_qdrant()),
            ServiceStatus(name="minio", reachable=self.object_store.is_reachable()),
        ]
        return SystemHealth(
            services=services,
            anthropic_configured=bool(settings.ANTHROPIC_API_KEY),
            sentry_configured=bool(settings.SENTRY_DSN),
            otel_configured=bool(settings.OTEL_EXPORTER_OTLP_ENDPOINT),
            whisper_model_cached=stt.is_model_cached(),
            piper_model_cached=tts.is_model_cached(),
        )

    async def _check_postgres(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def _check_redis(self) -> bool:
        try:
            return bool(await self.redis_client.ping())
        except Exception:
            return False

    def _check_qdrant(self) -> bool:
        try:
            get_qdrant_client().get_collections()
            return True
        except Exception:
            return False

    async def get_llm_usage_summary(self) -> LLMUsageSummary:
        totals = await LLMUsageRepository(self.session).totals_by_agent()
        return LLMUsageSummary(
            by_agent=[
                AgentUsageTotals(
                    agent_name=agent_name,
                    call_count=call_count,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
                for agent_name, call_count, input_tokens, output_tokens in totals
            ]
        )

    async def get_session_activity(self) -> SessionActivity:
        now = datetime.now(UTC)
        today = now.date()
        week_start = now - timedelta(days=7)

        sessions = await StudySessionRepository(self.session).list_all_since(week_start)
        sessions_today = sum(1 for s in sessions if s.studied_on.date() == today)
        active_users = {s.user_id for s in sessions}
        return SessionActivity(
            sessions_today=sessions_today,
            sessions_this_week=len(sessions),
            active_users_this_week=len(active_users),
        )

    async def list_error_logs(self, limit: int = 50) -> list[ErrorLogEntryRead]:
        entries = await ErrorLogRepository(self.session).list_recent(limit)
        return [ErrorLogEntryRead.model_validate(entry) for entry in entries]

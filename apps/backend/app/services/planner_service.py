"""Daily planner business logic: gathers the learner's current state, runs
the Planner Agent graph, and caches the result in Redis for the rest of the
day (the plan is deterministic for a given day + available_minutes, so
recomputing it on every dashboard refresh would be wasted DB/CPU work)."""
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.planner_agent import generate_daily_plan
from app.domain.schemas.planner import DailyPlan
from app.models.user_topic_progress import TopicStatus
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.topics_service import TopicsService

CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours — cheap to recompute, so no need to cache until midnight


@dataclass
class PlannerService:
    session: AsyncSession
    redis_client: redis.Redis

    def _cache_key(self, user_id: uuid.UUID, today: str, available_minutes: int) -> str:
        return f"planner:{user_id}:{today}:{available_minutes}"

    async def get_today_plan(self, user_id: uuid.UUID, available_minutes: int) -> DailyPlan:
        today = datetime.now(UTC).date()
        cache_key = self._cache_key(user_id, today.isoformat(), available_minutes)

        cached = await self.redis_client.get(cache_key)
        if cached is not None:
            return DailyPlan.model_validate_json(cached)

        vocab_due_count = await VocabularyRepository(self.session).count_due(user_id, today)
        topics = await TopicsService(self.session).list_for_user(user_id)
        weak_topic_count = sum(1 for t in topics if t.status != TopicStatus.MASTERED)

        blocks = generate_daily_plan(available_minutes, vocab_due_count, weak_topic_count)

        plan = DailyPlan(
            generated_for=today,
            available_minutes=available_minutes,
            vocab_due_count=vocab_due_count,
            weak_topic_count=weak_topic_count,
            blocks=blocks,
        )
        await self.redis_client.set(cache_key, plan.model_dump_json(), ex=CACHE_TTL_SECONDS)
        return plan

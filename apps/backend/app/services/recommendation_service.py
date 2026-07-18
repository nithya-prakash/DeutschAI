"""Recommendation Engine business logic: gathers vocab + topic candidates
from real per-user data and runs the Recommendation Agent to rank them.
Internal content only — see docs/schemas/recommendations.py docstring for
why podcasts/articles aren't part of this."""
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ml.forgetting_curve import days_since, retention_probability
from app.ai.recommendation_agent import rank_recommendations
from app.domain.schemas.recommendations import (
    RecommendationResult,
    RecommendedTopic,
    RecommendedVocab,
)
from app.models.user_topic_progress import TopicStatus
from app.repositories.memory_repository import MemoryRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.topics_service import TopicsService


@dataclass
class RecommendationService:
    session: AsyncSession

    async def get_recommendations(self, user_id: uuid.UUID) -> RecommendationResult:
        now = datetime.now(UTC)

        vocab_items = await VocabularyRepository(self.session).list_for_user(user_id)
        vocab_by_id = {item.id: item for item in vocab_items if item.last_reviewed_at is not None}
        vocab_candidates = [
            {
                "id": str(item.id),
                "german": item.german,
                "english": item.english,
                "retention": retention_probability(
                    item.ease_factor, item.interval_days, days_since(now, item.last_reviewed_at)
                ),
            }
            for item in vocab_by_id.values()
        ]

        mistake_counts = await MemoryRepository(self.session).count_by_topic_for_user(user_id)
        topics = await TopicsService(self.session).list_for_user(user_id)
        topic_candidates = [
            {
                "topic_id": str(topic.id),
                "topic_name": topic.name,
                "mistake_count": mistake_counts[topic.id],
            }
            for topic in topics
            if topic.status != TopicStatus.MASTERED and mistake_counts.get(topic.id, 0) > 0
        ]

        ranked_vocab, ranked_topics = rank_recommendations(vocab_candidates, topic_candidates)

        return RecommendationResult(
            vocab=[
                RecommendedVocab(
                    id=uuid.UUID(v["id"]),
                    german=v["german"],
                    english=v["english"],
                    retention_probability=v["retention"],
                    reason=(
                        f"Retention estimated at {round(v['retention'] * 100)}% "
                        "— review it soon"
                    ),
                )
                for v in ranked_vocab
            ],
            topics=[
                RecommendedTopic(
                    topic_id=uuid.UUID(t["topic_id"]),
                    topic_name=t["topic_name"],
                    reason=(
                        f"{t['mistake_count']} recorded mistake"
                        f"{'s' if t['mistake_count'] != 1 else ''} on this topic"
                    ),
                )
                for t in ranked_topics
            ],
        )

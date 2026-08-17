"""Analytics Engine: turns raw per-user history into skill scores, topic
rankings, a progress forecast, and habit-intelligence figures. No metric
here is shown unless there's real data behind it — missing data means
`None`/an empty list (see docs/ARCHITECTURE.md).
"""
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ml.forecasting import predict_milestone
from app.ai.ml.forgetting_curve import days_since, is_at_risk, retention_probability
from app.ai.ml.habit_model import best_study_day, consistency_score
from app.domain.schemas.dashboard import PredictedMilestone, SkillScores, TopicRanking
from app.models.user_topic_progress import TopicStatus
from app.repositories.memory_repository import MemoryRepository
from app.repositories.quiz_repository import QuizAttemptRepository
from app.repositories.speech_conversation_repository import SpeechConversationRepository
from app.repositories.user_topic_progress_repository import UserTopicProgressRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.topics_service import TopicsService

TOP_RANKED_TOPICS = 3


@dataclass
class AnalyticsResult:
    skill_scores: SkillScores
    weakest_topics: list[TopicRanking]
    strongest_topics: list[TopicRanking]
    predicted_milestone: PredictedMilestone | None
    consistency_score: float | None
    best_study_day: str | None
    vocab_at_risk_count: int


@dataclass
class AnalyticsService:
    session: AsyncSession

    async def get_analytics(
        self, user_id: uuid.UUID, session_tuples: list[tuple[datetime, int]]
    ) -> AnalyticsResult:
        """`session_tuples`: (studied_on, duration_minutes) for this user,
        fetched once by the caller (`DashboardService`) over a window wide
        enough to cover actual habit-intelligence history — not re-queried
        here, so this always sees the same data the caller does."""
        now = datetime.now(UTC)
        today = now.date()

        topics = await TopicsService(self.session).list_for_user(user_id)
        topic_names = {t.id: t.name for t in topics}

        vocabulary_score, vocab_at_risk_count = await self._vocabulary_score_and_at_risk_count(
            user_id, now
        )
        skill_scores, weakest, strongest = await self._skill_scores_and_rankings(
            user_id, topic_names, vocabulary_score
        )
        predicted_milestone = await self._predict_milestone(user_id, total_topics=len(topics))

        consistency = consistency_score(session_tuples, today) if session_tuples else None
        study_day = best_study_day(session_tuples)

        return AnalyticsResult(
            skill_scores=skill_scores,
            weakest_topics=weakest,
            strongest_topics=strongest,
            predicted_milestone=predicted_milestone,
            consistency_score=consistency,
            best_study_day=study_day,
            vocab_at_risk_count=vocab_at_risk_count,
        )

    async def _skill_scores_and_rankings(
        self,
        user_id: uuid.UUID,
        topic_names: dict[uuid.UUID, str],
        vocabulary_score: float | None,
    ) -> tuple[SkillScores, list[TopicRanking], list[TopicRanking]]:
        attempts = await QuizAttemptRepository(self.session).list_for_user_with_topic(user_id)
        mistake_counts = await MemoryRepository(self.session).count_by_topic_for_user(user_id)

        grammar_score = None
        accuracy_by_topic: dict[uuid.UUID, float] = {}
        if attempts:
            grammar_score = 100.0 * sum(1 for correct, _topic_id in attempts if correct) / len(
                attempts
            )
            per_topic: dict[uuid.UUID, list[bool]] = {}
            for correct, topic_id in attempts:
                per_topic.setdefault(topic_id, []).append(correct)
            accuracy_by_topic = {
                topic_id: 100.0 * sum(results) / len(results)
                for topic_id, results in per_topic.items()
            }

        ranked_topic_ids = set(accuracy_by_topic) | set(mistake_counts)
        rankings = [
            TopicRanking(
                topic_id=topic_id,
                topic_name=topic_names.get(topic_id, "Unknown topic"),
                mistake_count=mistake_counts.get(topic_id, 0),
                accuracy=accuracy_by_topic.get(topic_id),
            )
            for topic_id in ranked_topic_ids
        ]
        def _accuracy_or(ranking: TopicRanking, default: float) -> float:
            return ranking.accuracy if ranking.accuracy is not None else default

        weakest = sorted(rankings, key=lambda r: (-r.mistake_count, _accuracy_or(r, 100.0)))[
            :TOP_RANKED_TOPICS
        ]
        strongest = sorted(rankings, key=lambda r: (r.mistake_count, -_accuracy_or(r, 0.0)))[
            :TOP_RANKED_TOPICS
        ]

        speaking_score = await self._speaking_score(user_id)

        skill_scores = SkillScores(
            grammar=grammar_score, vocabulary=vocabulary_score, speaking=speaking_score
        )
        return skill_scores, weakest, strongest

    async def _vocabulary_score_and_at_risk_count(
        self, user_id: uuid.UUID, now: datetime
    ) -> tuple[float | None, int]:
        vocab_items = await VocabularyRepository(self.session).list_for_user(user_id)
        retentions = []
        at_risk_count = 0
        for item in vocab_items:
            if item.last_reviewed_at is None:
                continue  # never reviewed — no forgetting signal to compute yet
            retention = retention_probability(
                item.ease_factor, item.interval_days, days_since(now, item.last_reviewed_at)
            )
            retentions.append(retention)
            if is_at_risk(retention):
                at_risk_count += 1
        score = 100.0 * sum(retentions) / len(retentions) if retentions else None
        return score, at_risk_count

    async def _speaking_score(self, user_id: uuid.UUID) -> float | None:
        turns = await SpeechConversationRepository(self.session).list_scored_user_turns(user_id)
        scores = [
            (turn.grammar_score + turn.vocabulary_score) / 2
            for turn in turns
            if turn.grammar_score is not None and turn.vocabulary_score is not None
        ]
        return sum(scores) / len(scores) if scores else None

    async def _predict_milestone(
        self, user_id: uuid.UUID, total_topics: int
    ) -> PredictedMilestone | None:
        progress_rows = await UserTopicProgressRepository(self.session).list_for_user(user_id)
        mastery_dates = sorted(
            row.updated_at.date() for row in progress_rows if row.status == TopicStatus.MASTERED
        )
        if not mastery_dates:
            return None

        progress_points: list[tuple] = []
        cumulative = 0
        for d in mastery_dates:
            cumulative += 1
            if progress_points and progress_points[-1][0] == d:
                progress_points[-1] = (d, cumulative)
            else:
                progress_points.append((d, cumulative))

        forecast = predict_milestone(progress_points, total_topics=total_topics)
        if forecast is None:
            return None
        return PredictedMilestone(
            topics_remaining=forecast.topics_remaining, projected_date=forecast.projected_date
        )

"""Dashboard summary schema.

Ships real numbers for streak/study minutes/CEFR level, plus skill scores,
topic rankings, a progress forecast, habit intelligence, and motivation
messaging — computed by `AnalyticsService` / `MotivationService` from
actual usage data. Every field is nullable (or an empty list) exactly
where the underlying data doesn't exist yet for a given user, so the
frontend can render a clear gap instead of a placeholder number.
`locked_insights` lists what's genuinely still missing platform-wide
(listening/reading/writing have no scoring signal yet).
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.user import CEFRLevel


class DailyMinutes(BaseModel):
    date: date
    minutes: int


class SkillScores(BaseModel):
    """0-100 or `None` if that skill has no data yet for this user."""

    grammar: float | None
    vocabulary: float | None
    speaking: float | None


class TopicRanking(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    mistake_count: int
    accuracy: float | None


class PredictedMilestone(BaseModel):
    topics_remaining: int
    projected_date: date


class MotivationMessage(BaseModel):
    headline: str
    body: str
    suggested_minutes: int


class DashboardSummary(BaseModel):
    cefr_level: CEFRLevel
    member_since: datetime
    current_streak_days: int
    longest_streak_days: int
    total_study_minutes: int
    weekly_study_minutes: int
    last_12_weeks: list[DailyMinutes]
    skill_scores: SkillScores
    weakest_topics: list[TopicRanking]
    strongest_topics: list[TopicRanking]
    predicted_milestone: PredictedMilestone | None
    consistency_score: float | None
    best_study_day: str | None
    vocab_at_risk_count: int
    motivation_message: MotivationMessage | None
    locked_insights: list[str]

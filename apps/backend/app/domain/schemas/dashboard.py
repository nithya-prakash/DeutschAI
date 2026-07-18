"""Dashboard summary schema.

Phase 1 ships real numbers for what the platform actually tracks today
(streak, study minutes, CEFR level). Metrics that depend on later phases
(vocabulary/grammar mastery, skill scores, ML forecasts) are surfaced as
`locked_insights` so the UI can show them as "coming soon" instead of
fabricating numbers.
"""
from datetime import date, datetime

from pydantic import BaseModel

from app.models.user import CEFRLevel


class DailyMinutes(BaseModel):
    date: date
    minutes: int


class DashboardSummary(BaseModel):
    cefr_level: CEFRLevel
    member_since: datetime
    current_streak_days: int
    longest_streak_days: int
    total_study_minutes: int
    weekly_study_minutes: int
    last_12_weeks: list[DailyMinutes]
    locked_insights: list[str]

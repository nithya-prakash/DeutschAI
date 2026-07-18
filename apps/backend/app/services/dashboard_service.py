"""Dashboard summary computation.

Streak and weekly-minutes logic lives here rather than in the repository
(pure data access) or the API layer (transport only) — it's business logic
the Habit/Analytics engines will extend in later phases.
"""
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.dashboard import DailyMinutes, DashboardSummary
from app.repositories.study_session_repository import StudySessionRepository
from app.repositories.user_repository import UserRepository

WEEKS_OF_HISTORY = 12

# Metrics the platform will compute starting later phases. Kept explicit here
# (rather than silently omitted) so the frontend can render honest
# "coming soon" placeholders instead of fabricated numbers.
# NOTE: vocabulary/grammar tracking shipped in Phase 2 (see /vocabulary and
# /curriculum); raw mistake tracking shipped in Phase 3 (see the "Recent
# mistakes" card, backed by the Memory Agent) — both removed from this list
# accordingly rather than left stale. What's still missing is the *aggregate*
# analysis on top of that raw data.
LOCKED_INSIGHTS = [
    "Speaking / Listening / Reading / Writing scores (Phase 4/5)",
    "Predicted next milestone (Phase 5 — ML forecasting)",
    "Aggregated weakest/strongest topic ranking (Phase 5 — Analytics Engine)",
]


@dataclass
class DashboardService:
    session: AsyncSession

    async def get_summary(self, user_id: uuid.UUID) -> DashboardSummary:
        user_repo = UserRepository(self.session)
        session_repo = StudySessionRepository(self.session)

        user = await user_repo.get(user_id)
        if user is None:
            raise ValueError(f"user {user_id} not found")

        since = datetime.now(UTC) - timedelta(weeks=WEEKS_OF_HISTORY)
        sessions = await session_repo.list_for_user_since(user_id, since)

        minutes_by_day: dict[date, int] = {}
        for s in sessions:
            day = s.studied_on.date()
            minutes_by_day[day] = minutes_by_day.get(day, 0) + s.duration_minutes

        today = datetime.now(UTC).date()
        current_streak = self._current_streak(minutes_by_day, today)
        longest_streak = self._longest_streak(minutes_by_day, today)

        total_minutes = sum(minutes_by_day.values())
        week_start = today - timedelta(days=6)
        weekly_minutes = sum(m for d, m in minutes_by_day.items() if d >= week_start)

        last_12_weeks = [
            DailyMinutes(date=today - timedelta(days=offset), minutes=minutes_by_day.get(
                today - timedelta(days=offset), 0
            ))
            for offset in range(WEEKS_OF_HISTORY * 7 - 1, -1, -1)
        ]

        return DashboardSummary(
            cefr_level=user.cefr_level,
            member_since=user.created_at,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            total_study_minutes=total_minutes,
            weekly_study_minutes=weekly_minutes,
            last_12_weeks=last_12_weeks,
            locked_insights=LOCKED_INSIGHTS,
        )

    @staticmethod
    def _current_streak(minutes_by_day: dict[date, int], today: date) -> int:
        cursor = today if today in minutes_by_day else today - timedelta(days=1)
        streak = 0
        while cursor in minutes_by_day:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    @staticmethod
    def _longest_streak(minutes_by_day: dict[date, int], today: date) -> int:
        days = sorted(minutes_by_day.keys())
        if not days:
            return 0
        longest = run = 1
        for prev, curr in zip(days, days[1:], strict=False):
            if (curr - prev).days == 1:
                run += 1
            else:
                run = 1
            longest = max(longest, run)
        return max(longest, DashboardService._current_streak(minutes_by_day, today))

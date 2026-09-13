"""Dashboard summary computation.

Streak and weekly-minutes logic lives here; skill scores, topic
rankings, forecast, and habit-intelligence figures come from
`AnalyticsService`, and the motivation banner from `MotivationService` —
composed together into one `DashboardSummary` here, the single place the
`/dashboard/summary` endpoint reads from.
"""
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.dashboard import (
    DailyMinutes,
    DashboardSummary,
    MotivationMessage,
)
from app.repositories.study_session_repository import StudySessionRepository
from app.repositories.user_repository import UserRepository
from app.services.analytics_service import AnalyticsService
from app.services.motivation_service import get_motivation_message

WEEKS_OF_HISTORY = 12  # how far back the heatmap/weekly-minutes display goes
# How far back the underlying StudySession query goes — wider than the
# display window above so streak-longest-ever, habit intelligence, and the
# motivation message (which needs the learner's *actual* last session, not
# just one within the last 12 weeks) all see real history instead of an
# artificially truncated slice.
DATA_FETCH_DAYS = 365

# What's still genuinely missing platform-wide, kept explicit (rather than
# silently omitted) so the frontend renders a clear "coming soon" instead
# of a placeholder number. Empty now that every skill score (grammar,
# vocabulary, speaking, reading, listening, writing), topic rankings,
# forecasting, and habit intelligence all have a real exercise/signal behind
# them — kept as a list, not removed, so a future genuinely-locked insight
# has somewhere to go.
LOCKED_INSIGHTS: list[str] = []


@dataclass
class DashboardService:
    session: AsyncSession

    async def get_summary(self, user_id: uuid.UUID) -> DashboardSummary:
        user_repo = UserRepository(self.session)
        session_repo = StudySessionRepository(self.session)

        user = await user_repo.get(user_id)
        if user is None:
            raise ValueError(f"user {user_id} not found")

        since = datetime.now(UTC) - timedelta(days=DATA_FETCH_DAYS)
        sessions = await session_repo.list_for_user_since(user_id, since)

        minutes_by_day: dict[date, int] = {}
        for s in sessions:
            day = s.studied_on.date()
            minutes_by_day[day] = minutes_by_day.get(day, 0) + s.duration_minutes

        today = datetime.now(UTC).date()
        current_streak = self._current_streak(minutes_by_day, today)
        longest_streak = self._longest_streak(minutes_by_day, today)

        week_start = today - timedelta(days=6)
        weekly_minutes = sum(m for d, m in minutes_by_day.items() if d >= week_start)
        display_window_start = today - timedelta(weeks=WEEKS_OF_HISTORY)
        total_minutes = sum(m for d, m in minutes_by_day.items() if d >= display_window_start)

        last_12_weeks = [
            DailyMinutes(date=today - timedelta(days=offset), minutes=minutes_by_day.get(
                today - timedelta(days=offset), 0
            ))
            for offset in range(WEEKS_OF_HISTORY * 7 - 1, -1, -1)
        ]

        session_tuples = [(s.studied_on, s.duration_minutes) for s in sessions]
        analytics = await AnalyticsService(self.session).get_analytics(user_id, session_tuples)
        motivation = get_motivation_message(session_tuples, today)

        return DashboardSummary(
            cefr_level=user.cefr_level,
            member_since=user.created_at,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            total_study_minutes=total_minutes,
            weekly_study_minutes=weekly_minutes,
            last_12_weeks=last_12_weeks,
            skill_scores=analytics.skill_scores,
            weakest_topics=analytics.weakest_topics,
            strongest_topics=analytics.strongest_topics,
            predicted_milestone=analytics.predicted_milestone,
            consistency_score=analytics.consistency_score,
            best_study_day=analytics.best_study_day,
            vocab_at_risk_count=analytics.vocab_at_risk_count,
            motivation_message=(
                MotivationMessage(
                    headline=motivation.headline,
                    body=motivation.body,
                    suggested_minutes=motivation.suggested_minutes,
                )
                if motivation
                else None
            ),
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

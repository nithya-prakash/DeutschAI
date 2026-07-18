"""Habit Intelligence: consistency scoring and skip prediction from a user's
actual `StudySession` history — real weighted statistics computed from
logged dates, not a hardcoded "3 skips = at risk" style threshold.

Note: `StudySession.studied_on` is always written as `datetime.now(UTC)` at
log time (see the model), and `User` stores no timezone — so there's no
reliable local hour-of-day signal to report an "best time of day" without
risking a UTC hour that's actively misleading for the learner. Day-of-week
doesn't have that problem (a UTC-vs-local shift essentially never changes
which calendar day a session falls on), so habit intelligence here reports
the best study *day* rather than a clock hour.
"""
from datetime import date, datetime, timedelta

# Rolling window for the recency-weighted consistency score.
CONSISTENCY_WINDOW_DAYS = 30
# Exponential recency decay per day — recent days count more than older ones.
RECENCY_DECAY = 0.95

# Below this many distinct days of history, a skip-probability estimate
# would be fit to noise rather than a real pattern.
MIN_HISTORY_DAYS_FOR_SKIP_MODEL = 14
MIN_SESSIONS_FOR_BEST_DAY = 5

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _studied_dates(sessions: list[tuple[datetime, int]]) -> set[date]:
    return {studied_on.date() for studied_on, _minutes in sessions}


def consistency_score(sessions: list[tuple[datetime, int]], as_of: date) -> float:
    """0-100: recency-weighted fraction of the last `CONSISTENCY_WINDOW_DAYS`
    that had a logged session — a day 10 days ago counts for less than
    yesterday, so a recent lapse pulls the score down faster than an old one
    pulls it up."""
    studied = _studied_dates(sessions)
    weighted_studied = 0.0
    weighted_total = 0.0
    for days_ago in range(CONSISTENCY_WINDOW_DAYS):
        day = as_of - timedelta(days=days_ago)
        weight = RECENCY_DECAY**days_ago
        weighted_total += weight
        if day in studied:
            weighted_studied += weight
    return 100.0 * weighted_studied / weighted_total if weighted_total else 0.0


def skip_probability(sessions: list[tuple[datetime, int]], target_date: date) -> float | None:
    """Probability the learner will *not* study on `target_date`, blending
    their historical rate for that day-of-week with their recent overall
    consistency. `None` if there isn't enough history yet to fit either."""
    studied = _studied_dates(sessions)
    if not studied:
        return None

    earliest = min(studied)
    history_days = (target_date - earliest).days
    if history_days < MIN_HISTORY_DAYS_FOR_SKIP_MODEL:
        return None

    same_weekday_days = [
        earliest + timedelta(days=offset)
        for offset in range(history_days + 1)
        if (earliest + timedelta(days=offset)).weekday() == target_date.weekday()
    ]
    weekday_study_rate = sum(1 for d in same_weekday_days if d in studied) / len(same_weekday_days)

    recent_consistency = consistency_score(sessions, target_date - timedelta(days=1)) / 100.0

    study_probability = 0.5 * weekday_study_rate + 0.5 * recent_consistency
    return 1.0 - study_probability


def best_study_day(sessions: list[tuple[datetime, int]]) -> str | None:
    """The day of the week the learner most consistently studies on, by
    historical frequency. `None` under a minimum sample size."""
    if len(sessions) < MIN_SESSIONS_FOR_BEST_DAY:
        return None

    counts = [0] * 7
    for studied_on, _minutes in sessions:
        counts[studied_on.weekday()] += 1

    best_index = max(range(7), key=lambda i: counts[i])
    return WEEKDAY_NAMES[best_index] if counts[best_index] > 0 else None

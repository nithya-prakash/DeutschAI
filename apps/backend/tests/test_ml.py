"""Unit tests for app/ai/ml/ — pure functions, no DB, no LLM."""
from datetime import UTC, date, datetime, timedelta

from app.ai.ml.forecasting import predict_milestone
from app.ai.ml.forgetting_curve import days_since, is_at_risk, retention_probability
from app.ai.ml.habit_model import best_study_day, consistency_score, skip_probability
from app.models.vocabulary_item import DEFAULT_EASE_FACTOR

# --- forgetting_curve ---


def test_retention_is_perfect_right_after_review():
    r = retention_probability(DEFAULT_EASE_FACTOR, interval_days=10, days_since_last_review=0)
    assert r == 1.0


def test_retention_decays_with_time():
    soon = retention_probability(DEFAULT_EASE_FACTOR, interval_days=10, days_since_last_review=5)
    later = retention_probability(DEFAULT_EASE_FACTOR, interval_days=10, days_since_last_review=20)
    assert 0 < later < soon < 1


def test_higher_ease_factor_decays_slower():
    low_ease = retention_probability(1.5, interval_days=10, days_since_last_review=15)
    high_ease = retention_probability(4.0, interval_days=10, days_since_last_review=15)
    assert high_ease > low_ease


def test_is_at_risk_threshold():
    assert is_at_risk(0.3) is True
    assert is_at_risk(0.9) is False


def test_days_since_handles_naive_datetime_as_utc():
    # SQLite (the test suite's engine) hands back naive datetimes even for
    # tz-aware columns — this must not raise, and must match the aware case.
    now = datetime(2026, 1, 15, tzinfo=UTC)
    naive_ten_days_ago = datetime(2026, 1, 5)
    aware_ten_days_ago = datetime(2026, 1, 5, tzinfo=UTC)
    assert days_since(now, naive_ten_days_ago) == 10
    assert days_since(now, naive_ten_days_ago) == days_since(now, aware_ten_days_ago)


# --- habit_model ---


def _session(days_ago: int, minutes: int = 30) -> tuple[datetime, int]:
    return (datetime.now(UTC) - timedelta(days=days_ago), minutes)


def test_consistency_score_perfect_streak():
    today = date.today()
    sessions = [_session(days_ago=i) for i in range(30)]
    score = consistency_score(sessions, today)
    assert score == 100.0


def test_consistency_score_no_history():
    assert consistency_score([], date.today()) == 0.0


def test_consistency_score_recent_gap_hurts_more_than_old_gap():
    today = date.today()
    # Studied every day except yesterday.
    recent_gap = [_session(days_ago=i) for i in range(30) if i != 1]
    # Studied every day except 29 days ago.
    old_gap = [_session(days_ago=i) for i in range(30) if i != 29]
    assert consistency_score(recent_gap, today) < consistency_score(old_gap, today)


def test_skip_probability_none_without_enough_history():
    today = date.today()
    sessions = [_session(days_ago=i) for i in range(3)]
    assert skip_probability(sessions, today + timedelta(days=1)) is None


def test_skip_probability_low_for_consistent_studier():
    today = date.today()
    sessions = [_session(days_ago=i) for i in range(30)]
    prob = skip_probability(sessions, today + timedelta(days=1))
    assert prob is not None
    assert prob < 0.3


def test_best_study_day_none_with_too_few_sessions():
    assert best_study_day([_session(0), _session(1)]) is None


def test_best_study_day_picks_most_frequent_weekday():
    # Build sessions concentrated on a single actual weekday so this is
    # robust to whatever "today" is when the test runs.
    monday = date(2026, 1, 5)  # a Monday
    sessions = [
        (datetime.combine(monday + timedelta(weeks=i), datetime.min.time(), tzinfo=UTC), 30)
        for i in range(6)
    ]
    assert best_study_day(sessions) == "Monday"


# --- forecasting ---


def test_predict_milestone_none_with_single_point():
    result = predict_milestone([(date(2026, 1, 1), 2)], total_topics=16)
    assert result is None


def test_predict_milestone_none_when_already_complete():
    points = [(date(2026, 1, 1), 8), (date(2026, 1, 15), 16)]
    assert predict_milestone(points, total_topics=16) is None


def test_predict_milestone_none_on_flat_trend():
    points = [(date(2026, 1, 1), 4), (date(2026, 1, 15), 4)]
    assert predict_milestone(points, total_topics=16) is None


def test_predict_milestone_projects_forward_on_real_progress():
    points = [(date(2026, 1, 1), 2), (date(2026, 1, 11), 4), (date(2026, 1, 21), 6)]
    forecast = predict_milestone(points, total_topics=16)
    assert forecast is not None
    assert forecast.topics_remaining == 10
    assert forecast.projected_date > date(2026, 1, 21)

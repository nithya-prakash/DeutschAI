"""Pure unit tests for the SM-2 scheduler — no DB, no app, no async."""
from datetime import date

from app.services.spaced_repetition import (
    DEFAULT_EASE_FACTOR,
    MIN_EASE_FACTOR,
    ReviewQuality,
    SchedulingState,
    schedule_next_review,
)

TODAY = date(2026, 1, 1)


def fresh_state() -> SchedulingState:
    return SchedulingState(ease_factor=DEFAULT_EASE_FACTOR, interval_days=0, repetitions=0)


def test_first_successful_review_sets_interval_to_one_day():
    new_state, next_due = schedule_next_review(fresh_state(), ReviewQuality.GOOD, TODAY)
    assert new_state.interval_days == 1
    assert new_state.repetitions == 1
    assert next_due == date(2026, 1, 2)


def test_second_successful_review_sets_interval_to_six_days():
    state, _ = schedule_next_review(fresh_state(), ReviewQuality.GOOD, TODAY)
    state, next_due = schedule_next_review(state, ReviewQuality.GOOD, TODAY)
    assert state.interval_days == 6
    assert state.repetitions == 2


def test_third_successful_review_multiplies_by_ease_factor():
    state, _ = schedule_next_review(fresh_state(), ReviewQuality.GOOD, TODAY)
    state, _ = schedule_next_review(state, ReviewQuality.GOOD, TODAY)
    ease_before_third_review = state.ease_factor
    state, _ = schedule_next_review(state, ReviewQuality.GOOD, TODAY)
    assert state.repetitions == 3
    assert state.interval_days == round(6 * ease_before_third_review)


def test_failed_review_resets_repetitions_and_interval():
    state, _ = schedule_next_review(fresh_state(), ReviewQuality.GOOD, TODAY)
    state, _ = schedule_next_review(state, ReviewQuality.GOOD, TODAY)
    state, next_due = schedule_next_review(state, ReviewQuality.AGAIN, TODAY)
    assert state.repetitions == 0
    assert state.interval_days == 1
    assert next_due == date(2026, 1, 2)


def test_easy_reviews_increase_ease_factor():
    state, _ = schedule_next_review(fresh_state(), ReviewQuality.EASY, TODAY)
    assert state.ease_factor > DEFAULT_EASE_FACTOR


def test_hard_reviews_decrease_ease_factor():
    state, _ = schedule_next_review(fresh_state(), ReviewQuality.HARD, TODAY)
    assert state.ease_factor < DEFAULT_EASE_FACTOR


def test_ease_factor_never_drops_below_minimum():
    state = fresh_state()
    for _ in range(20):
        state, _ = schedule_next_review(state, ReviewQuality.HARD, TODAY)
    assert state.ease_factor >= MIN_EASE_FACTOR

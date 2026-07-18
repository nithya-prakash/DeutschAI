"""SM-2 spaced-repetition scheduling.

A deterministic, well-established scheduling algorithm (SuperMemo 2) — not an
ML model. It replaces the fixed-interval flashcard schedule (1/3/7/14/30/60
days regardless of performance) with one driven by review history and a
per-word "ease": harder words get shorter intervals and lower ease, easier
words get longer intervals and higher ease, and a failed review resets
progress rather than just repeating the same fixed step.

Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""
from dataclasses import dataclass
from datetime import date, timedelta
from enum import IntEnum

MIN_EASE_FACTOR = 1.3
DEFAULT_EASE_FACTOR = 2.5


class ReviewQuality(IntEnum):
    """How well the user recalled the word, 0 (blackout) to 5 (perfect)."""

    AGAIN = 1
    HARD = 3
    GOOD = 4
    EASY = 5


@dataclass(frozen=True)
class SchedulingState:
    ease_factor: float
    interval_days: int
    repetitions: int


def schedule_next_review(
    state: SchedulingState, quality: ReviewQuality, today: date
) -> tuple[SchedulingState, date]:
    """Apply one SM-2 review step. Returns the new state and next due date."""
    if quality < ReviewQuality.HARD:
        # A failed recall resets progress but keeps the (slightly penalized) ease,
        # so a word that's failed repeatedly still gets progressively harder to earn back.
        new_repetitions = 0
        new_interval = 1
    else:
        if state.repetitions == 0:
            new_interval = 1
        elif state.repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(state.interval_days * state.ease_factor)
        new_repetitions = state.repetitions + 1

    ease_delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    new_ease = max(MIN_EASE_FACTOR, state.ease_factor + ease_delta)

    new_state = SchedulingState(
        ease_factor=new_ease, interval_days=new_interval, repetitions=new_repetitions
    )
    return new_state, today + timedelta(days=new_interval)

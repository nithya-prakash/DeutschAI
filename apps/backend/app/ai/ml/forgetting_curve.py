"""Vocabulary forgetting-curve model.

Grounded entirely in each word's existing SM-2 state (`ease_factor`,
`interval_days`, `last_reviewed_at`) rather than a dedicated review-history
table — that state already encodes how well-learned the word is, so a
retention estimate can be computed today with no schema change.

Ebbinghaus-style exponential decay: R = e^(-t/S), where `t` is days since
the last review and `S` ("stability") scales with how strong the word's
SM-2 state already is — a longer proven interval or higher ease factor
means slower decay.
"""
import math
from datetime import UTC, datetime

from app.models.vocabulary_item import DEFAULT_EASE_FACTOR

# Below this retention estimate, a word is flagged "at risk" of being
# forgotten before its next scheduled review.
AT_RISK_THRESHOLD = 0.5


def retention_probability(
    ease_factor: float, interval_days: int, days_since_last_review: int
) -> float:
    """Estimated probability (0-1) the word is still remembered right now."""
    stability = max(interval_days, 1) * (ease_factor / DEFAULT_EASE_FACTOR)
    return math.exp(-days_since_last_review / stability)


def is_at_risk(retention: float) -> bool:
    return retention < AT_RISK_THRESHOLD


def days_since(now: datetime, last_reviewed_at: datetime) -> int:
    """Days between `now` and a DB-sourced timestamp. SQLite (the test
    suite's engine) hands back naive datetimes even for `DateTime(timezone=
    True)` columns, while Postgres preserves tzinfo — so a naive value here
    is assumed UTC rather than left to fail the subtraction outright."""
    if last_reviewed_at.tzinfo is None:
        last_reviewed_at = last_reviewed_at.replace(tzinfo=UTC)
    return (now - last_reviewed_at).days

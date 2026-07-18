"""Motivation Agent: deterministic streak-recovery messaging.

Templates, not an LLM call — the message space here is small and bounded
(a handful of "how long has it been" buckets), so a rule picks a canned,
non-guilt-tripping message rather than reaching for generation. Always
"reduce and re-invite": every message pairs an encouraging tone with a
*smaller* suggested minutes figure for today, never a bigger one and never
language that shames the gap.
"""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class MotivationMessage:
    headline: str
    body: str
    suggested_minutes: int


_WELCOME_BACK = MotivationMessage(
    headline="Welcome back",
    body=(
        "A couple of days off is completely normal — let's ease back in with "
        "something light today."
    ),
    suggested_minutes=15,
)
_PICK_IT_BACK_UP = MotivationMessage(
    headline="Let's pick this back up",
    body=(
        "It's been a few days. No need to catch up all at once — a short "
        "session today keeps things moving."
    ),
    suggested_minutes=10,
)
_FRESH_START = MotivationMessage(
    headline="Fresh start",
    body=(
        "It's been a while, and that's okay. Starting again with just a few "
        "minutes counts for a lot."
    ),
    suggested_minutes=10,
)


def get_motivation_message(
    sessions: list[tuple[datetime, int]], today: date
) -> MotivationMessage | None:
    """`None` when there's nothing to say: no history yet (nothing to
    "recover" from), or the learner studied yesterday or today (actively on
    track, no message needed)."""
    if not sessions:
        return None

    last_studied = max(studied_on.date() for studied_on, _minutes in sessions)
    days_since = (today - last_studied).days

    if days_since <= 1:
        return None
    if days_since <= 3:
        return _WELCOME_BACK
    if days_since <= 7:
        return _PICK_IT_BACK_UP
    return _FRESH_START

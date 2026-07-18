"""Daily planner schemas."""
from datetime import date

from pydantic import BaseModel


class PlanBlock(BaseModel):
    activity: str
    minutes: int
    reason: str


class DailyPlan(BaseModel):
    generated_for: date
    available_minutes: int
    vocab_due_count: int
    weak_topic_count: int
    blocks: list[PlanBlock]

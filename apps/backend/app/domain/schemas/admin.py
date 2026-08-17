"""Admin panel response schemas. Every field here is either real data
already in the DB, a real reachability check performed at request time, or
a zero/empty value where no data exists yet (see docs/ARCHITECTURE.md)."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceStatus(BaseModel):
    name: str
    reachable: bool


class SystemHealth(BaseModel):
    services: list[ServiceStatus]
    anthropic_configured: bool
    sentry_configured: bool
    otel_configured: bool
    whisper_model_cached: bool
    piper_model_cached: bool


class AgentUsageTotals(BaseModel):
    agent_name: str
    call_count: int
    input_tokens: int
    output_tokens: int


class LLMUsageSummary(BaseModel):
    by_agent: list[AgentUsageTotals]


class SessionActivity(BaseModel):
    sessions_today: int
    sessions_this_week: int
    active_users_this_week: int


class ErrorLogEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    method: str
    path: str
    exception_type: str
    message: str

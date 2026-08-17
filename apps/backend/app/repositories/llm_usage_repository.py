"""Data access for LLMUsageEvent — backs the admin panel's "LLM token spend"."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_usage_event import LLMUsageEvent
from app.repositories.base import BaseRepository


class LLMUsageRepository(BaseRepository[LLMUsageEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LLMUsageEvent)

    async def totals_by_agent(self) -> list[tuple[str, int, int, int]]:
        """(agent_name, call_count, total_input_tokens, total_output_tokens),
        across all users — real counts, empty until ANTHROPIC_API_KEY is set
        and calls actually happen."""
        result = await self.session.execute(
            select(
                LLMUsageEvent.agent_name,
                func.count(),
                func.coalesce(func.sum(LLMUsageEvent.input_tokens), 0),
                func.coalesce(func.sum(LLMUsageEvent.output_tokens), 0),
            ).group_by(LLMUsageEvent.agent_name)
        )
        return list(result.all())

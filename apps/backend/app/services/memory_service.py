"""Memory Agent business logic.

Memories are written internally by the Assessment Agent (a wrong quiz
answer becomes a `MISTAKE` memory tied to that question's topic) and surfaced
to the user read-only as a "recent mistakes" feed. There's no user-facing
"add a memory" endpoint yet. A deeper feedback loop — memories influencing
the Planner Agent's weak-topic weighting — is a natural next step once
there's usage data to tune it against.
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.memory import MemoryRead
from app.models.ai_memory import AIMemory, MemoryType
from app.repositories.memory_repository import MemoryRepository


@dataclass
class MemoryService:
    session: AsyncSession

    async def record(
        self,
        user_id: uuid.UUID,
        memory_type: MemoryType,
        content: str,
        related_topic_id: uuid.UUID | None = None,
    ) -> AIMemory:
        memory = AIMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            related_topic_id=related_topic_id,
        )
        return await MemoryRepository(self.session).create(memory)

    async def list_recent(self, user_id: uuid.UUID, limit: int = 20) -> list[MemoryRead]:
        memories = await MemoryRepository(self.session).list_recent_for_user(user_id, limit)
        return [
            MemoryRead(
                id=m.id,
                memory_type=m.memory_type,
                content=m.content,
                related_topic_name=m.related_topic.name if m.related_topic else None,
                created_at=m.created_at,
            )
            for m in memories
        ]

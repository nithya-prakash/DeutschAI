"""Generic async repository base class.

Concrete repositories extend this for entity-specific queries. Keeping
data access behind repositories means services never import SQLAlchemy
`select()` directly — swapping persistence (or mocking it in tests) only
touches this layer.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import Base


class BaseRepository[ModelType: Base]:
    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def get(self, id_: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, id_)

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

"""Memory Agent endpoints — read-only "recent mistakes" feed."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.memory import MemoryRead
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryRead])
async def list_recent_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MemoryRead]:
    return await MemoryService(db).list_recent(current_user.id)

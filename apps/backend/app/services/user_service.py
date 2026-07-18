"""User profile business logic."""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.user import UserUpdate
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserNotFoundError(Exception):
    pass


@dataclass
class UserService:
    session: AsyncSession

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        repo = UserRepository(self.session)
        user = await repo.get(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        return user

    async def update_profile(self, user_id: uuid.UUID, payload: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

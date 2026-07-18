"""Authentication business logic: registration and credential verification."""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.domain.schemas.auth import TokenResponse
from app.domain.schemas.user import UserCreate
from app.models.user import User
from app.repositories.user_repository import UserRepository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


@dataclass
class AuthService:
    session: AsyncSession

    async def register(self, payload: UserCreate) -> User:
        repo = UserRepository(self.session)
        existing = await repo.get_by_email(payload.email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(payload.email)

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            target_language=payload.target_language,
        )
        user = await repo.create(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        repo = UserRepository(self.session)
        user = await repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()
        return user

    @staticmethod
    def issue_tokens(user: User) -> TokenResponse:
        subject = str(user.id)
        return TokenResponse(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

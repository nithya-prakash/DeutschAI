"""Shared FastAPI dependencies: DB session, current-user resolution, Redis."""
import uuid

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import TokenType, decode_token
from app.infrastructure.database.session import get_db
from app.infrastructure.object_store.minio_client import ObjectStore, get_object_store
from app.infrastructure.redis.client import get_redis_client
from app.models.user import User
from app.repositories.user_repository import UserRepository

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.type != TokenType.ACCESS:
        raise credentials_error

    try:
        user_id = uuid.UUID(payload.sub)
    except ValueError:
        raise credentials_error from None

    user = await UserRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise credentials_error

    return user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def get_redis() -> redis.Redis:
    return get_redis_client()


def get_object_storage() -> ObjectStore:
    return get_object_store()

"""Authentication endpoints: register, login, refresh."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, create_access_token, create_refresh_token, decode_token
from app.domain.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.domain.schemas.user import UserCreate, UserRead
from app.infrastructure.database.session import get_db
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    service = AuthService(db)
    try:
        user = await service.register(payload)
    except EmailAlreadyRegisteredError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from err
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    try:
        user = await service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        ) from err
    return service.issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    token_payload = decode_token(payload.refresh_token)
    if token_payload is None or token_payload.type != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    return TokenResponse(
        access_token=create_access_token(token_payload.sub),
        refresh_token=create_refresh_token(token_payload.sub),
    )

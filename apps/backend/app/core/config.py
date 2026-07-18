"""Application configuration.

Centralized settings loaded from environment variables (or a `.env` file in
local development). Every other module reads configuration through this
object rather than calling `os.environ` directly, so config has one source
of truth and is trivially mockable in tests.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    PROJECT_NAME: str = "DeutschAI"
    ENVIRONMENT: Literal["local", "test", "staging", "production"] = "local"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- Security ---
    SECRET_KEY: str = Field(..., description="Used to sign JWTs. Must be set in production.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # --- Database ---
    POSTGRES_USER: str = "deutschai"
    POSTGRES_PASSWORD: str = "deutschai"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "deutschai"
    DATABASE_URI: PostgresDsn | None = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_uri(cls, v: str | None, info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return (
            f"postgresql+asyncpg://{data['POSTGRES_USER']}:{data['POSTGRES_PASSWORD']}"
            f"@{data['POSTGRES_HOST']}:{data['POSTGRES_PORT']}/{data['POSTGRES_DB']}"
        )

    # --- Redis ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URI: RedisDsn | None = None

    @field_validator("REDIS_URI", mode="before")
    @classmethod
    def assemble_redis_uri(cls, v: str | None, info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return f"redis://{data['REDIS_HOST']}:{data['REDIS_PORT']}/{data['REDIS_DB']}"

    # --- Vector DB (RAG knowledge base) ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "grammar_knowledge_base"

    # --- LLM (Tutor Agent) ---
    # Left unset in local dev by default. The Tutor Agent fails loudly with a
    # clear "not configured" error if this is missing rather than faking a
    # response — see app/ai/tutor_agent.py.
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-5"

    # --- Object storage (Phase 4: speech audio blobs) ---
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "deutschai"
    MINIO_SECRET_KEY: str = "deutschai123"
    MINIO_BUCKET: str = "deutschai-media"

    # --- Speech engine (Phase 4) ---
    # faster-whisper model size — "base" is a CPU-friendly tradeoff for local dev;
    # bump to "small"/"medium" for better accuracy if the host has the CPU to spare.
    WHISPER_MODEL_SIZE: str = "base"
    # Piper voice name (rhasspy/piper-voices on Hugging Face), downloaded and
    # cached locally on first use — same pattern as fastembed's embedding model.
    PIPER_VOICE: str = "de_DE-thorsten-medium"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (env is read once per process)."""
    return Settings()

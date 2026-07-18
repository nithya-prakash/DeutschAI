"""Qdrant client factory."""
from functools import lru_cache

from qdrant_client import QdrantClient

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

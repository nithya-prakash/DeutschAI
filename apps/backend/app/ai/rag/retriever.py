"""Semantic retrieval over the ingested grammar knowledge base."""
from dataclasses import dataclass

from qdrant_client import QdrantClient

from app.ai.rag.embedder import embed_query
from app.core.config import get_settings
from app.infrastructure.vector_store.qdrant_client import get_qdrant_client

settings = get_settings()

DEFAULT_TOP_K = 4


@dataclass(frozen=True)
class RetrievedChunk:
    topic_name: str
    text: str
    score: float


def retrieve(
    query: str, top_k: int = DEFAULT_TOP_K, client: QdrantClient | None = None
) -> list[RetrievedChunk]:
    """Embed `query` and return the top-k most similar knowledge-base chunks."""
    client = client or get_qdrant_client()
    vector = embed_query(query)

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=vector,
        limit=top_k,
    ).points

    return [
        RetrievedChunk(
            topic_name=point.payload["topic_name"],
            text=point.payload["text"],
            score=point.score,
        )
        for point in results
    ]

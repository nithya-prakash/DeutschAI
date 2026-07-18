"""Knowledge base ingestion pipeline: markdown files -> chunks -> embeddings -> Qdrant.

Run once (and again whenever `knowledge_base/*.md` changes) via:

    docker compose exec backend python -m app.ai.rag.ingest

Idempotent: each chunk's point ID is derived deterministically from its
source file and index, so re-running overwrites existing points instead of
duplicating them.
"""
import logging
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.ai.rag.embedder import VECTOR_SIZE, embed_texts
from app.core.config import get_settings
from app.infrastructure.vector_store.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)
settings = get_settings()

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"
MAX_CHUNK_CHARS = 800

# Namespace for deterministic chunk IDs, so re-ingestion overwrites rather
# than duplicates points.
_ID_NAMESPACE = uuid.UUID("6f6a1b2c-6e2e-4b8b-9d1a-6a2f6b6e6a2f")


def parse_document(text: str) -> tuple[str, str]:
    """Split a knowledge-base file into (topic_name, body). The topic name is
    the first Markdown H1 heading (`# Topic Name`); the body is everything after."""
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("Knowledge base file must start with a '# Topic Name' heading")
    topic_name = lines[0][2:].strip()
    body = "\n".join(lines[1:]).strip()
    return topic_name, body


def chunk_text(body: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Greedily merge blank-line-separated paragraphs into chunks up to
    `max_chars`, never splitting a paragraph across two chunks (unless a
    single paragraph alone exceeds max_chars, in which case it stays whole —
    our source paragraphs are always short enough that this doesn't happen)."""
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


def load_documents() -> list[tuple[str, str]]:
    """Returns (topic_name, body) for every .md file in the knowledge base dir."""
    return [
        parse_document(path.read_text(encoding="utf-8"))
        for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))
    ]


def ensure_collection(client: QdrantClient) -> None:
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def ingest_knowledge_base(client: QdrantClient | None = None) -> int:
    """Chunk + embed + upsert every knowledge-base document. Returns the
    number of chunks ingested."""
    client = client or get_qdrant_client()
    ensure_collection(client)

    documents = load_documents()
    points: list[PointStruct] = []
    for source_index, (topic_name, body) in enumerate(documents):
        chunks = chunk_text(body)
        vectors = embed_texts(chunks)
        for chunk_index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            point_id = str(uuid.uuid5(_ID_NAMESPACE, f"{topic_name}:{chunk_index}"))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "topic_name": topic_name,
                        "chunk_index": chunk_index,
                        "source_index": source_index,
                        "text": chunk,
                    },
                )
            )

    if points:
        client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    logger.info("Ingested %d chunks from %d documents", len(points), len(documents))
    return len(points)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    count = ingest_knowledge_base()
    print(f"Ingested {count} chunks into Qdrant collection '{settings.QDRANT_COLLECTION}'.")


if __name__ == "__main__":
    main()

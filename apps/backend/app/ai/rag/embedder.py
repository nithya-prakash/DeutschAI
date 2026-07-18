"""Local embedding model wrapper.

Uses `fastembed` (ONNX runtime, no torch) rather than sentence-transformers —
a much lighter dependency footprint for the exact same job, and it's the
library Qdrant itself publishes for pairing with their vector DB. Runs fully
locally: no embedding API key, no per-call cost, works offline once the model
is cached.
"""
from functools import lru_cache
from pathlib import Path

from fastembed import TextEmbedding

# Smallest multilingual model fastembed ships — our corpus mixes German and
# English in short passages, so multilingual support matters more than the
# marginal quality gain from the larger e5-large/mpnet-base variants.
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTOR_SIZE = 384

_CACHE_DIR = Path(__file__).resolve().parents[3] / ".fastembed_cache"


@lru_cache
def get_embedder() -> TextEmbedding:
    _CACHE_DIR.mkdir(exist_ok=True)
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(_CACHE_DIR))


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one 384-dim vector per input text."""
    model = get_embedder()
    return [vector.tolist() for vector in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    """Embed a single query string (e5-style models use a distinct query prefix
    in principle; paraphrase-multilingual-MiniLM doesn't require one)."""
    return embed_texts([text])[0]

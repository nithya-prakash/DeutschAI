"""RAG pipeline integration test: real embeddings (fastembed, cached locally)
against an in-memory Qdrant instance — no external Qdrant service needed,
the same "in-memory instead of a live service" trick used for Postgres via
SQLite elsewhere in this test suite."""
import pytest
from qdrant_client import QdrantClient

from app.ai.rag.ingest import ingest_knowledge_base
from app.ai.rag.retriever import retrieve


@pytest.fixture(scope="module")
def ingested_client() -> QdrantClient:
    """Ingest the real knowledge base into a fresh in-memory Qdrant once per
    module — embedding all 40-ish chunks is the slow part, so sharing it
    across the tests in this file keeps the suite fast."""
    client = QdrantClient(":memory:")
    count = ingest_knowledge_base(client=client)
    assert count > 0
    return client


def test_ingestion_produces_chunks_for_every_topic(ingested_client):
    results = retrieve("Tell me about German grammar in general", top_k=50, client=ingested_client)
    topic_names = {r.topic_name for r in results}
    assert "Negation (nicht/kein)" in topic_names
    assert "Akkusativ case" in topic_names
    assert len(topic_names) >= 10


def test_retrieve_finds_the_right_topic_for_a_targeted_question(ingested_client):
    results = retrieve("When do I use kein instead of nicht?", client=ingested_client)
    assert results
    assert results[0].topic_name == "Negation (nicht/kein)"


def test_retrieve_respects_top_k(ingested_client):
    results = retrieve("How does German word order work?", top_k=2, client=ingested_client)
    assert len(results) == 2


def test_retrieve_scores_are_descending(ingested_client):
    results = retrieve("How do I conjugate regular verbs?", top_k=5, client=ingested_client)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)

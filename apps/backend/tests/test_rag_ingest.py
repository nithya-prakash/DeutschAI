"""Pure unit tests for the ingestion pipeline's parsing/chunking — no Qdrant,
no embeddings needed."""
import pytest

from app.ai.rag.ingest import chunk_text, load_documents, parse_document


def test_parse_document_extracts_topic_name_and_body():
    text = "# My Topic\n\nSome content here.\n\nMore content."
    topic_name, body = parse_document(text)
    assert topic_name == "My Topic"
    assert body == "Some content here.\n\nMore content."


def test_parse_document_requires_h1_heading():
    with pytest.raises(ValueError, match="Topic Name"):
        parse_document("Not a heading\n\nSome content.")


def test_chunk_text_keeps_short_body_as_one_chunk():
    body = "Paragraph one.\n\nParagraph two."
    chunks = chunk_text(body, max_chars=800)
    assert chunks == ["Paragraph one.\n\nParagraph two."]


def test_chunk_text_splits_when_exceeding_max_chars():
    paragraphs = [f"Paragraph {i} " + "x" * 100 for i in range(10)]
    body = "\n\n".join(paragraphs)
    chunks = chunk_text(body, max_chars=300)
    assert len(chunks) > 1
    # Every paragraph survives somewhere, none are split mid-paragraph.
    rejoined = "\n\n".join(chunks)
    for paragraph in paragraphs:
        assert paragraph in rejoined


def test_chunk_text_never_exceeds_max_chars_except_single_long_paragraph():
    body = "\n\n".join(f"Short para {i}." for i in range(20))
    chunks = chunk_text(body, max_chars=100)
    assert all(len(c) <= 100 for c in chunks)


def test_load_documents_reads_all_sixteen_grammar_topics():
    documents = load_documents()
    assert len(documents) == 16
    topic_names = {name for name, _ in documents}
    assert "Negation (nicht/kein)" in topic_names
    assert "Akkusativ case" in topic_names
    # Every document actually has body content.
    assert all(len(body) > 50 for _, body in documents)

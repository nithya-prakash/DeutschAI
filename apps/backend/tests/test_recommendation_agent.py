"""Recommendation Agent graph-level tests (no DB, no LLM)."""
from app.ai.recommendation_agent import rank_recommendations


def test_ranks_vocab_by_lowest_retention_first():
    vocab = [
        {"id": "a", "german": "Hund", "english": "dog", "retention": 0.9},
        {"id": "b", "german": "Katze", "english": "cat", "retention": 0.3},
        {"id": "c", "german": "Vogel", "english": "bird", "retention": 0.6},
    ]
    ranked_vocab, _ = rank_recommendations(vocab, [])
    assert [v["id"] for v in ranked_vocab] == ["b", "c", "a"]


def test_ranks_topics_by_highest_mistake_count_first():
    topics = [
        {"topic_id": "1", "topic_name": "Akkusativ", "mistake_count": 2},
        {"topic_id": "2", "topic_name": "Perfekt", "mistake_count": 7},
        {"topic_id": "3", "topic_name": "Dativ", "mistake_count": 4},
    ]
    _, ranked_topics = rank_recommendations([], topics)
    assert [t["topic_id"] for t in ranked_topics] == ["2", "3", "1"]


def test_truncates_to_top_n():
    vocab = [
        {"id": str(i), "german": f"w{i}", "english": f"e{i}", "retention": i / 10}
        for i in range(10)
    ]
    ranked_vocab, _ = rank_recommendations(vocab, [], top_n=3)
    assert len(ranked_vocab) == 3
    assert [v["id"] for v in ranked_vocab] == ["0", "1", "2"]


def test_empty_candidates_return_empty_lists():
    ranked_vocab, ranked_topics = rank_recommendations([], [])
    assert ranked_vocab == []
    assert ranked_topics == []

"""Recommendation Agent — ranks which specific vocab words and grammar
topics a learner should focus on next.

Built as a LangGraph graph (assess -> rank -> render), the same shape as
`app/ai/planner_agent.py`, and for the same reason: ranking pre-fetched
candidates by a real, precomputed score (forgetting-curve retention, mistake
counts) doesn't need generation, so every node here is a deterministic
Python function — no LLM call needed for this component.
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

DEFAULT_TOP_N = 5


class VocabCandidate(TypedDict):
    id: str
    german: str
    english: str
    retention: float


class TopicCandidate(TypedDict):
    topic_id: str
    topic_name: str
    mistake_count: int


class RecommendationState(TypedDict):
    vocab_candidates: list[VocabCandidate]
    topic_candidates: list[TopicCandidate]
    top_n: int
    ranked_vocab: list[VocabCandidate]
    ranked_topics: list[TopicCandidate]


def _assess(state: RecommendationState) -> RecommendationState:
    """Inputs are already fetched by the caller (RecommendationService), so
    this node just marks the graph's entry point — mirrors
    `planner_agent._assess`."""
    return state


def _rank(state: RecommendationState) -> RecommendationState:
    ranked_vocab = sorted(state["vocab_candidates"], key=lambda v: v["retention"])
    ranked_topics = sorted(
        state["topic_candidates"], key=lambda t: t["mistake_count"], reverse=True
    )
    return {**state, "ranked_vocab": ranked_vocab, "ranked_topics": ranked_topics}


def _render(state: RecommendationState) -> RecommendationState:
    top_n = state["top_n"]
    return {
        **state,
        "ranked_vocab": state["ranked_vocab"][:top_n],
        "ranked_topics": state["ranked_topics"][:top_n],
    }


def _build_graph():
    graph = StateGraph(RecommendationState)
    graph.add_node("assess", _assess)
    graph.add_node("rank", _rank)
    graph.add_node("render", _render)
    graph.set_entry_point("assess")
    graph.add_edge("assess", "rank")
    graph.add_edge("rank", "render")
    graph.add_edge("render", END)
    return graph.compile()


_compiled_graph = _build_graph()


def rank_recommendations(
    vocab_candidates: list[VocabCandidate],
    topic_candidates: list[TopicCandidate],
    top_n: int = DEFAULT_TOP_N,
) -> tuple[list[VocabCandidate], list[TopicCandidate]]:
    """Run the Recommendation Agent graph and return (ranked vocab, ranked
    topics), each truncated to `top_n`."""
    result = _compiled_graph.invoke(
        {
            "vocab_candidates": vocab_candidates,
            "topic_candidates": topic_candidates,
            "top_n": top_n,
            "ranked_vocab": [],
            "ranked_topics": [],
        }
    )
    return result["ranked_vocab"], result["ranked_topics"]

"""Planner Agent — turns available study time + weak spots into a daily plan.

Built as a LangGraph graph so the orchestration shape (assess -> allocate ->
render) matches every other agent this platform will add, even though every
node here is a deterministic Python function with no LLM call. That's a
deliberate choice, not a placeholder: allocating study minutes across
activities doesn't need generation, so an LLM would add cost and
non-determinism for no benefit. The Tutor Agent is where an LLM-backed
node earns its place — inserting one here (e.g. a "narrate" node that turns
`blocks` into a conversational summary) is a one-node change to the graph
below, not a rewrite.
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

# Base time-allocation weights for a session, before adjusting for the
# learner's actual state. Mirrors the suggested-routine split for a ~45 min
# session: vocab review, grammar, listening, speaking.
BASE_WEIGHTS: dict[str, float] = {
    "vocab": 0.33,
    "grammar": 0.33,
    "listening": 0.22,
    "speaking": 0.12,
}

# Thresholds past which the plan leans harder into one activity.
HIGH_VOCAB_DUE_THRESHOLD = 10
HIGH_WEAK_TOPIC_THRESHOLD = 5
VOCAB_BOOST = 0.15
GRAMMAR_BOOST = 0.15

MIN_BLOCK_MINUTES = 5


class PlannerState(TypedDict):
    available_minutes: int
    vocab_due_count: int
    weak_topic_count: int
    weights: dict[str, float]
    blocks: list[dict]


def _assess(state: PlannerState) -> PlannerState:
    """Placeholder for signal-gathering — inputs are already computed by the
    caller (PlannerService), so this node just marks the graph's entry point."""
    return state


def _allocate(state: PlannerState) -> PlannerState:
    weights = dict(BASE_WEIGHTS)
    if state["vocab_due_count"] > HIGH_VOCAB_DUE_THRESHOLD:
        weights["vocab"] += VOCAB_BOOST
    if state["weak_topic_count"] > HIGH_WEAK_TOPIC_THRESHOLD:
        weights["grammar"] += GRAMMAR_BOOST

    total_weight = sum(weights.values())
    normalized = {activity: w / total_weight for activity, w in weights.items()}
    return {**state, "weights": normalized}


def _render(state: PlannerState) -> PlannerState:
    total_minutes = state["available_minutes"]
    weights = state["weights"]

    # Round each share, then let the largest bucket absorb any rounding drift
    # so the blocks always sum to exactly `available_minutes`.
    raw_minutes = {activity: round(w * total_minutes) for activity, w in weights.items()}
    drift = total_minutes - sum(raw_minutes.values())
    if drift != 0:
        largest = max(raw_minutes, key=lambda a: raw_minutes[a])
        raw_minutes[largest] += drift

    reasons = {
        "vocab": (
            f"{state['vocab_due_count']} words are due for review"
            if state["vocab_due_count"] > 0
            else "Keep building your vocabulary"
        ),
        "grammar": (
            f"{state['weak_topic_count']} topics still need work"
            if state["weak_topic_count"] > 0
            else "Reinforce what you've already learned"
        ),
        "listening": "Build listening comprehension",
        "speaking": "Practice speaking or shadowing",
    }

    blocks = [
        {"activity": activity, "minutes": minutes, "reason": reasons[activity]}
        for activity, minutes in raw_minutes.items()
        if minutes >= MIN_BLOCK_MINUTES
    ]
    return {**state, "blocks": blocks}


def _build_graph():
    graph = StateGraph(PlannerState)
    graph.add_node("assess", _assess)
    graph.add_node("allocate", _allocate)
    graph.add_node("render", _render)
    graph.set_entry_point("assess")
    graph.add_edge("assess", "allocate")
    graph.add_edge("allocate", "render")
    graph.add_edge("render", END)
    return graph.compile()


_compiled_graph = _build_graph()


def generate_daily_plan(
    available_minutes: int, vocab_due_count: int, weak_topic_count: int
) -> list[dict]:
    """Run the Planner Agent graph and return its ordered list of plan blocks."""
    result = _compiled_graph.invoke(
        {
            "available_minutes": available_minutes,
            "vocab_due_count": vocab_due_count,
            "weak_topic_count": weak_topic_count,
            "weights": {},
            "blocks": [],
        }
    )
    return result["blocks"]

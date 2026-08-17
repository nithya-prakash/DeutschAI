"""Conversation Agent — turn-taking spoken dialogue practice.

A 2-node LangGraph graph (generate -> parse). One Claude call per user turn
does double duty: continue a natural German conversation at the learner's
CEFR level, and score the grammar/vocabulary of what the learner just said.
Reuses `get_chat_model` from `tutor_agent.py` rather than duplicating the
Anthropic client factory — same LLM, same "fail loudly if unconfigured"
contract (callers catch `tutor_agent.LLMNotConfiguredError`).

Pronunciation/fluency are deliberately not scored here — Claude has no audio
input, so there's no real signal for either; the API surfaces them as
locked rather than inventing a number (see docs/ARCHITECTURE.md).
"""
import json
from typing import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.ai.tutor_agent import get_chat_model

SYSTEM_PROMPT_TEMPLATE = """You are a friendly German conversation partner inside DeutschAI, \
practicing spoken dialogue with a learner at CEFR level {cefr_level}. Keep the conversation \
natural and in German, at a vocabulary/grammar complexity matched to {cefr_level}.

You also evaluate the learner's most recent message for grammar and vocabulary correctness \
(0-100 each, where 100 is flawless for their level) and give brief, encouraging feedback \
(1-2 sentences, in English, on what was good and what to fix).

Respond with ONLY a JSON object, no other text:
{{"reply": "<your next line of dialogue, in German>", "grammar_score": <0-100>, \
"vocabulary_score": <0-100>, "feedback": "<brief feedback in English>"}}

Conversation so far:
{history}
"""


class ConversationTurnState(TypedDict):
    user_utterance: str
    cefr_level: str
    history: list[tuple[str, str]]  # (role, text) pairs, oldest first
    raw_response: str
    reply: str
    grammar_score: int | None
    vocabulary_score: int | None
    feedback: str | None
    input_tokens: int
    output_tokens: int


def _format_history(history: list[tuple[str, str]]) -> str:
    if not history:
        return "(this is the first message)"
    return "\n".join(f"{role}: {text}" for role, text in history)


def _build_generate_node(chat_model: BaseChatModel):
    def _generate(state: ConversationTurnState) -> ConversationTurnState:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            cefr_level=state["cefr_level"], history=_format_history(state["history"])
        )
        response = chat_model.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=state["user_utterance"])]
        )
        raw = response.content if isinstance(response.content, str) else str(response.content)
        # `usage_metadata` isn't set on the fake chat models the graph-level
        # tests use — defaulting to 0 there is correct, not a fallback for a
        # real-call failure.
        usage = getattr(response, "usage_metadata", None) or {}
        return {
            **state,
            "raw_response": raw,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }

    return _generate


def _parse_node(state: ConversationTurnState) -> ConversationTurnState:
    raw = state["raw_response"].strip()
    # Claude sometimes wraps JSON in a markdown code fence despite instructions.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        return {
            **state,
            "reply": str(data["reply"]),
            "grammar_score": int(data["grammar_score"]),
            "vocabulary_score": int(data["vocabulary_score"]),
            "feedback": str(data["feedback"]),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Fallback: keep the raw text as the reply rather than inventing
        # scores the model didn't actually produce.
        return {
            **state,
            "reply": state["raw_response"].strip(),
            "grammar_score": None,
            "vocabulary_score": None,
            "feedback": None,
        }


def build_conversation_graph(chat_model: BaseChatModel):
    """Compile the generate->parse graph against a given chat model. Taking
    the chat model as a parameter (rather than reaching for a global) is
    what makes this testable without an API key, exactly like
    `tutor_agent.build_tutor_graph`."""
    graph = StateGraph(ConversationTurnState)
    graph.add_node("generate", _build_generate_node(chat_model))
    graph.add_node("parse", _parse_node)
    graph.set_entry_point("generate")
    graph.add_edge("generate", "parse")
    graph.add_edge("parse", END)
    return graph.compile()


def run_conversation_turn(
    user_utterance: str, cefr_level: str, history: list[tuple[str, str]]
) -> ConversationTurnState:
    """Run the Conversation Agent graph against the real, configured chat
    model. Raises tutor_agent.LLMNotConfiguredError if ANTHROPIC_API_KEY
    isn't set."""
    graph = build_conversation_graph(get_chat_model())
    return graph.invoke(
        {
            "user_utterance": user_utterance,
            "cefr_level": cefr_level,
            "history": history,
            "raw_response": "",
            "reply": "",
            "grammar_score": None,
            "vocabulary_score": None,
            "feedback": None,
            "input_tokens": 0,
            "output_tokens": 0,
        }
    )

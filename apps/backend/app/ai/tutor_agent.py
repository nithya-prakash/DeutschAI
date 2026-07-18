"""Tutor Agent — answers grammar/vocabulary questions grounded in the RAG
knowledge base, tailored to the learner's CEFR level.

A 2-node LangGraph graph (retrieve -> generate). Unlike the Planner Agent,
this one genuinely needs generation — explaining a grammar point in plain
language, simplified to the right level, isn't something a rule-based system
can do. That means it genuinely needs `ANTHROPIC_API_KEY` configured.

Fails loudly rather than faking a response: `get_chat_model()` raises
`LLMNotConfiguredError` if the key is missing, checked lazily (at call time,
not import time) so the rest of the app works fine with no key set — only
`/tutor/ask` is affected, and it surfaces this as a clear HTTP 503.
"""
from functools import lru_cache
from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.ai.rag.retriever import RetrievedChunk, retrieve
from app.core.config import get_settings

settings = get_settings()

SYSTEM_PROMPT_TEMPLATE = """You are the Tutor Agent inside DeutschAI, an app that \
teaches German to a learner at CEFR level {cefr_level}. Explain grammar and \
vocabulary clearly, simply, and encouragingly.

Ground your answer in the reference material below — it comes from the app's own \
curated A1 grammar notes. If the reference material doesn't cover the question, say \
so plainly rather than inventing rules you're not sure of; you may still use your \
general knowledge of German in that case, but flag that it's outside the app's own \
material.

Keep answers short (a few sentences plus a brief example), matched to a \
{cefr_level} learner's vocabulary — don't introduce grammar concepts far beyond \
their level unless they specifically ask.

Reference material:
{context}
"""


class LLMNotConfiguredError(Exception):
    """Raised when the Tutor Agent is asked to generate but no API key is set."""


class TutorState(TypedDict):
    question: str
    cefr_level: str
    context_chunks: list[RetrievedChunk]
    answer: str
    input_tokens: int
    output_tokens: int


@lru_cache
def get_chat_model() -> BaseChatModel:
    if not settings.ANTHROPIC_API_KEY:
        raise LLMNotConfiguredError(
            "ANTHROPIC_API_KEY is not set — the Tutor Agent needs a real LLM to generate "
            "grounded answers. Set it in .env to enable /tutor/ask."
        )
    return ChatAnthropic(model=settings.ANTHROPIC_MODEL, api_key=settings.ANTHROPIC_API_KEY)


def _retrieve_node(state: TutorState) -> TutorState:
    chunks = retrieve(state["question"])
    return {**state, "context_chunks": chunks}


def _build_generate_node(chat_model: BaseChatModel):
    def _generate(state: TutorState) -> TutorState:
        context = "\n\n".join(
            f"[{c.topic_name}] {c.text}" for c in state["context_chunks"]
        ) or "(no matching reference material found)"

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            cefr_level=state["cefr_level"], context=context
        )
        response = chat_model.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=state["question"])]
        )
        answer = response.content if isinstance(response.content, str) else str(response.content)
        # `usage_metadata` isn't set on the fake chat models the graph-level
        # tests use — defaulting to 0 there is correct, not a fallback for a
        # real-call failure.
        usage = getattr(response, "usage_metadata", None) or {}
        return {
            **state,
            "answer": answer,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }

    return _generate


def build_tutor_graph(chat_model: BaseChatModel):
    """Compile the retrieve->generate graph against a given chat model.

    Taking the chat model as a parameter (rather than reaching for a global)
    is what makes this testable without an API key: tests pass a fake
    `BaseChatModel` and exercise retrieval + prompt assembly for real.
    """
    graph = StateGraph(TutorState)
    graph.add_node("retrieve", _retrieve_node)
    graph.add_node("generate", _build_generate_node(chat_model))
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


def ask_tutor(question: str, cefr_level: str) -> TutorState:
    """Run the Tutor Agent graph against the real, configured chat model.
    Raises LLMNotConfiguredError if ANTHROPIC_API_KEY isn't set."""
    graph = build_tutor_graph(get_chat_model())
    return graph.invoke(
        {
            "question": question,
            "cefr_level": cefr_level,
            "context_chunks": [],
            "answer": "",
            "input_tokens": 0,
            "output_tokens": 0,
        }
    )

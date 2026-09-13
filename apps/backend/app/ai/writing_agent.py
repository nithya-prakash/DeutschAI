"""Writing Agent — grades a learner's written submission against a prompt.

A 2-node LangGraph graph (generate -> parse), structurally identical to
conversation_agent.py: one Claude call grades grammar, vocabulary, and task
completion (0-100 each) plus brief feedback. Reuses `get_chat_model` from
tutor_agent.py rather than duplicating the Anthropic client factory — same
LLM, same "fail loudly if unconfigured" contract (callers catch
tutor_agent.LLMNotConfiguredError).
"""
import json
from typing import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.ai.tutor_agent import get_chat_model

SYSTEM_PROMPT_TEMPLATE = """You are a German writing evaluator inside DeutschAI, grading a \
learner's written response to a prompt, at CEFR level {cefr_level}.

Evaluate the submission on three 0-100 scales (100 is flawless for their level):
- grammar_score: grammatical correctness
- vocabulary_score: vocabulary range and appropriateness
- task_completion_score: how well the submission actually answers/completes the prompt

Also give brief, encouraging feedback (1-2 sentences, in English, on what was good and what to fix).

Respond with ONLY a JSON object, no other text:
{{"grammar_score": <0-100>, "vocabulary_score": <0-100>, "task_completion_score": <0-100>, \
"feedback": "<brief feedback in English>"}}

Prompt given to the learner:
{prompt_text}

Learner's submission:
{submitted_text}
"""


class WritingGradingState(TypedDict):
    prompt_text: str
    submitted_text: str
    cefr_level: str
    raw_response: str
    grammar_score: int | None
    vocabulary_score: int | None
    task_completion_score: int | None
    feedback: str | None
    input_tokens: int
    output_tokens: int


def _build_generate_node(chat_model: BaseChatModel):
    def _generate(state: WritingGradingState) -> WritingGradingState:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            cefr_level=state["cefr_level"],
            prompt_text=state["prompt_text"],
            submitted_text=state["submitted_text"],
        )
        response = chat_model.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=state["submitted_text"])]
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


def _parse_node(state: WritingGradingState) -> WritingGradingState:
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
            "grammar_score": int(data["grammar_score"]),
            "vocabulary_score": int(data["vocabulary_score"]),
            "task_completion_score": int(data["task_completion_score"]),
            "feedback": str(data["feedback"]),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Leave every score/feedback null rather than inventing a value the
        # model didn't actually produce.
        return {
            **state,
            "grammar_score": None,
            "vocabulary_score": None,
            "task_completion_score": None,
            "feedback": None,
        }


def build_writing_graph(chat_model: BaseChatModel):
    """Compile the generate->parse graph against a given chat model — same
    DI-for-testability shape as build_conversation_graph/build_tutor_graph."""
    graph = StateGraph(WritingGradingState)
    graph.add_node("generate", _build_generate_node(chat_model))
    graph.add_node("parse", _parse_node)
    graph.set_entry_point("generate")
    graph.add_edge("generate", "parse")
    graph.add_edge("parse", END)
    return graph.compile()


def run_writing_grading(
    prompt_text: str, submitted_text: str, cefr_level: str
) -> WritingGradingState:
    """Run the Writing Agent graph against the real, configured chat model.
    Raises tutor_agent.LLMNotConfiguredError if ANTHROPIC_API_KEY isn't set."""
    graph = build_writing_graph(get_chat_model())
    return graph.invoke(
        {
            "prompt_text": prompt_text,
            "submitted_text": submitted_text,
            "cefr_level": cefr_level,
            "raw_response": "",
            "grammar_score": None,
            "vocabulary_score": None,
            "task_completion_score": None,
            "feedback": None,
            "input_tokens": 0,
            "output_tokens": 0,
        }
    )

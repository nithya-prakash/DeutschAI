"""Writing Agent tests — graph-level only (no network, no API key),
mirroring tests/test_conversation_agent.py's FakeChatModel pattern."""
from types import SimpleNamespace

from app.ai.writing_agent import build_writing_graph


class FakeChatModel:
    def __init__(self, content: str) -> None:
        self.content = content
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return SimpleNamespace(content=self.content)


def _base_state():
    return {
        "prompt_text": "Beschreibe deinen Tag.",
        "submitted_text": "Ich bin um sieben Uhr aufgestanden.",
        "cefr_level": "A2",
        "raw_response": "",
        "grammar_score": None,
        "vocabulary_score": None,
        "task_completion_score": None,
        "feedback": None,
        "input_tokens": 0,
        "output_tokens": 0,
    }


def test_writing_graph_parses_well_formed_json():
    fake_model = FakeChatModel(
        '{"grammar_score": 80, "vocabulary_score": 70, "task_completion_score": 90, '
        '"feedback": "Good structure, minor grammar slip."}'
    )

    graph = build_writing_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["grammar_score"] == 80
    assert result["vocabulary_score"] == 70
    assert result["task_completion_score"] == 90
    assert "structure" in result["feedback"]
    # FakeChatModel doesn't set usage_metadata — 0 is the correct default.
    assert result["input_tokens"] == 0
    assert result["output_tokens"] == 0

    system_message = fake_model.last_messages[0]
    assert "A2" in system_message.content
    assert "Beschreibe deinen Tag." in system_message.content


def test_writing_graph_handles_markdown_fenced_json():
    fake_model = FakeChatModel(
        '```json\n{"grammar_score": 60, "vocabulary_score": 55, '
        '"task_completion_score": 65, "feedback": "Needs work."}\n```'
    )

    graph = build_writing_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["grammar_score"] == 60
    assert result["task_completion_score"] == 65


def test_writing_graph_falls_back_on_unparseable_response():
    fake_model = FakeChatModel("Sorry, I can't grade that right now.")

    graph = build_writing_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["grammar_score"] is None
    assert result["vocabulary_score"] is None
    assert result["task_completion_score"] is None
    assert result["feedback"] is None

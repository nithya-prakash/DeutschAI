"""Conversation Agent tests — graph-level only (no network, no API key),
mirroring tests/test_tutor.py's FakeChatModel pattern."""
from types import SimpleNamespace

from app.ai.conversation_agent import build_conversation_graph


class FakeChatModel:
    def __init__(self, content: str) -> None:
        self.content = content
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return SimpleNamespace(content=self.content)


def _base_state(user_utterance: str = "Ich habe gestern ins Kino gegangen."):
    return {
        "user_utterance": user_utterance,
        "cefr_level": "A2",
        "history": [],
        "raw_response": "",
        "reply": "",
        "grammar_score": None,
        "vocabulary_score": None,
        "feedback": None,
        "input_tokens": 0,
        "output_tokens": 0,
    }


def test_conversation_graph_parses_well_formed_json():
    fake_model = FakeChatModel(
        '{"reply": "Welchen Film hast du gesehen?", "grammar_score": 70, '
        '"vocabulary_score": 85, "feedback": "Good vocabulary, but it should be '
        '\\"bin gegangen\\", not \\"habe gegangen\\"."}'
    )

    graph = build_conversation_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["reply"] == "Welchen Film hast du gesehen?"
    assert result["grammar_score"] == 70
    assert result["vocabulary_score"] == 85
    assert "bin gegangen" in result["feedback"]
    # FakeChatModel doesn't set usage_metadata — 0 is the correct default,
    # not a masked failure (see conversation_agent._build_generate_node).
    assert result["input_tokens"] == 0
    assert result["output_tokens"] == 0

    system_message = fake_model.last_messages[0]
    assert "A2" in system_message.content


def test_conversation_graph_handles_markdown_fenced_json():
    fake_model = FakeChatModel(
        '```json\n{"reply": "Schön!", "grammar_score": 90, '
        '"vocabulary_score": 90, "feedback": "Well done."}\n```'
    )

    graph = build_conversation_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["reply"] == "Schön!"
    assert result["grammar_score"] == 90


def test_conversation_graph_falls_back_on_unparseable_response():
    fake_model = FakeChatModel("Sorry, I can't help with that right now.")

    graph = build_conversation_graph(fake_model)
    result = graph.invoke(_base_state())

    assert result["reply"] == "Sorry, I can't help with that right now."
    assert result["grammar_score"] is None
    assert result["vocabulary_score"] is None
    assert result["feedback"] is None


def test_conversation_graph_includes_history_in_prompt():
    fake_model = FakeChatModel(
        '{"reply": "ok", "grammar_score": 50, "vocabulary_score": 50, "feedback": "ok"}'
    )

    graph = build_conversation_graph(fake_model)
    state = _base_state()
    state["history"] = [("user", "Hallo!"), ("assistant", "Hallo, wie geht's?")]
    graph.invoke(state)

    system_message = fake_model.last_messages[0]
    assert "Hallo!" in system_message.content
    assert "Hallo, wie geht's?" in system_message.content

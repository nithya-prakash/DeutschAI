"""Tutor Agent tests.

Split into two layers:
- Graph-level: a fake chat model + monkeypatched retrieval, so prompt
  assembly and state flow are verified with zero external dependencies.
- Endpoint-level: `app.services.tutor_service.ask_tutor` is monkeypatched so
  conversation persistence (creation, message ordering, ownership) is
  verified without needing a real Anthropic API key — except for the one
  test that deliberately exercises the real, unconfigured path and expects
  the honest 503.
"""
from types import SimpleNamespace

import pytest

from app.ai.rag.retriever import RetrievedChunk
from app.ai.tutor_agent import (
    LLMNotConfiguredError,
    build_tutor_graph,
    get_active_model_name,
    get_chat_model,
    settings,
)


class FakeChatModel:
    def __init__(self, answer: str = "This is a fake grounded answer.") -> None:
        self.answer = answer
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return SimpleNamespace(content=self.answer)


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


# --- Graph-level tests (no network, no API key) ---


def test_get_chat_model_raises_without_api_key():
    get_chat_model.cache_clear()
    with pytest.raises(LLMNotConfiguredError):
        get_chat_model()


def test_get_chat_model_openai_without_base_url_or_key_raises(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "LLM_BASE_URL", None)
    monkeypatch.setattr(settings, "LLM_API_KEY", None)
    get_chat_model.cache_clear()
    with pytest.raises(LLMNotConfiguredError, match="LLM_PROVIDER=openai"):
        get_chat_model()
    get_chat_model.cache_clear()


def test_get_chat_model_openai_with_base_url_returns_chat_openai(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setattr(settings, "LLM_MODEL", "llama3.2")
    get_chat_model.cache_clear()
    model = get_chat_model()
    # Real ChatOpenAI construction (no network call) — confirms the local
    # server URL and model name were actually wired through, not just that
    # no exception was raised.
    assert model.openai_api_base == "http://localhost:11434/v1"
    assert model.model_name == "llama3.2"
    get_chat_model.cache_clear()


def test_get_active_model_name_reflects_provider(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-5")
    assert get_active_model_name() == "claude-sonnet-5"

    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "LLM_MODEL", "llama3.2")
    assert get_active_model_name() == "llama3.2"


def test_tutor_graph_retrieves_and_generates(monkeypatch):
    fake_chunks = [
        RetrievedChunk(
            topic_name="Negation (nicht/kein)",
            text="kein negates a noun that would otherwise carry ein/eine.",
            score=0.9,
        )
    ]
    monkeypatch.setattr(
        "app.ai.tutor_agent.retrieve", lambda question, top_k=4: fake_chunks
    )
    fake_model = FakeChatModel("Use kein for nouns without an article.")

    graph = build_tutor_graph(fake_model)
    result = graph.invoke(
        {"question": "kein vs nicht?", "cefr_level": "A1", "context_chunks": [], "answer": ""}
    )

    assert result["answer"] == "Use kein for nouns without an article."
    assert result["context_chunks"] == fake_chunks

    system_message = fake_model.last_messages[0]
    assert "A1" in system_message.content
    assert "Negation" in system_message.content


def test_tutor_graph_handles_no_matching_context(monkeypatch):
    monkeypatch.setattr("app.ai.tutor_agent.retrieve", lambda question, top_k=4: [])
    fake_model = FakeChatModel("I don't have specific material on that.")

    graph = build_tutor_graph(fake_model)
    result = graph.invoke(
        {
            "question": "What's the weather like?",
            "cefr_level": "B1",
            "context_chunks": [],
            "answer": "",
        }
    )

    assert result["context_chunks"] == []
    system_message = fake_model.last_messages[0]
    assert "no matching reference material" in system_message.content


# --- Endpoint-level tests ---


async def test_ask_tutor_without_api_key_returns_503(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.post(
        "/api/v1/tutor/ask",
        json={"question": "Was ist Akkusativ?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_ask_tutor_persists_conversation(client, user_payload, monkeypatch):
    def fake_ask_tutor(question: str, cefr_level: str):
        chunk = RetrievedChunk(topic_name="Negation (nicht/kein)", text="…", score=0.8)
        return {
            "question": question,
            "cefr_level": cefr_level,
            "context_chunks": [chunk],
            "answer": f"Here's the answer to: {question}",
            "input_tokens": 42,
            "output_tokens": 17,
        }

    monkeypatch.setattr("app.services.tutor_service.ask_tutor", fake_ask_tutor)

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/api/v1/tutor/ask", json={"question": "kein vs nicht?"}, headers=headers
    )
    assert first.status_code == 200
    body = first.json()
    assert body["answer"] == "Here's the answer to: kein vs nicht?"
    assert body["sources"] == ["Negation (nicht/kein)"]
    conversation_id = body["conversation_id"]

    # Follow-up in the same conversation.
    second = await client.post(
        "/api/v1/tutor/ask",
        json={"question": "And Akkusativ?", "conversation_id": conversation_id},
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id

    thread = await client.get(f"/api/v1/tutor/conversations/{conversation_id}", headers=headers)
    assert thread.status_code == 200
    messages = thread.json()["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    assert messages[0]["content"] == "kein vs nicht?"
    assert messages[2]["content"] == "And Akkusativ?"

    summaries = await client.get("/api/v1/tutor/conversations", headers=headers)
    assert summaries.status_code == 200
    assert len(summaries.json()) == 1
    assert summaries.json()[0]["message_count"] == 4


async def test_cannot_access_another_users_conversation(client, user_payload, monkeypatch):
    def fake_ask_tutor(question: str, cefr_level: str):
        return {
            "question": question,
            "cefr_level": cefr_level,
            "context_chunks": [],
            "answer": "ok",
            "input_tokens": 10,
            "output_tokens": 5,
        }

    monkeypatch.setattr("app.services.tutor_service.ask_tutor", fake_ask_tutor)

    token_a = await _register_and_login(client, user_payload)
    created = await client.post(
        "/api/v1/tutor/ask",
        json={"question": "hi"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    conversation_id = created.json()["conversation_id"]

    other_user = {
        "email": "other-tutor@example.com",
        "password": "supersecret123",
        "full_name": "Other User",
    }
    token_b = await _register_and_login(client, other_user)

    response = await client.get(
        f"/api/v1/tutor/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404

"""Conversation Mode tests.

Split the same way as tests/test_tutor.py:
- Wrapper-level: fake underlying STT/TTS model objects, so `transcribe`/
  `synthesize` are verified without loading real model weights.
- Endpoint-level: `transcribe_audio`/`synthesize_speech`/
  `run_conversation_turn` are monkeypatched so turn persistence (creation,
  ordering, ownership, scores) is verified without a real Anthropic API key
  or real audio models — except the one test that deliberately exercises
  the real, unconfigured LLM path and expects the honest 503.
"""
from types import SimpleNamespace

from app.ai.speech.stt import transcribe
from app.ai.speech.tts import synthesize

# --- Wrapper-level tests (no network, no model download) ---


class FakeWhisperModel:
    def transcribe(self, audio_path: str, language: str):
        segments = [SimpleNamespace(text="Hallo"), SimpleNamespace(text=" Welt.")]
        return segments, SimpleNamespace(language=language)


def test_transcribe_joins_segment_text():
    text = transcribe(FakeWhisperModel(), b"fake-audio-bytes")
    assert text == "Hallo Welt."


class FakeVoice:
    def synthesize(self, text: str) -> bytes:
        return b"RIFF....WAVEfake-audio-for:" + text.encode("utf-8")


def test_synthesize_delegates_to_the_voice():
    audio_bytes = synthesize(FakeVoice(), "Hallo Welt")
    assert audio_bytes == b"RIFF....WAVEfake-audio-for:Hallo Welt"


# --- Endpoint-level tests ---


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


def _fake_conversation_turn(reply="Welchen Film hast du gesehen?", grammar=70, vocab=85):
    def _run(user_utterance: str, cefr_level: str, history):
        return {
            "reply": reply,
            "grammar_score": grammar,
            "vocabulary_score": vocab,
            "feedback": "Almost — should be 'bin gegangen', not 'habe gegangen'.",
            "input_tokens": 30,
            "output_tokens": 20,
        }

    return _run


async def test_submit_turn_without_api_key_returns_503(client, user_payload, monkeypatch):
    monkeypatch.setattr(
        "app.services.speech_service.transcribe_audio", lambda audio_bytes: "Hallo"
    )

    token = await _register_and_login(client, user_payload)
    response = await client.post(
        "/api/v1/speech/turns",
        files={"audio": ("clip.webm", b"fake-audio-bytes", "audio/webm")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_submit_turn_rejects_empty_audio(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.post(
        "/api/v1/speech/turns",
        files={"audio": ("clip.webm", b"", "audio/webm")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


async def test_submit_turn_persists_conversation_and_scores(client, user_payload, monkeypatch):
    monkeypatch.setattr(
        "app.services.speech_service.transcribe_audio",
        lambda audio_bytes: "Ich habe gestern ins Kino gegangen.",
    )
    monkeypatch.setattr(
        "app.services.speech_service.run_conversation_turn", _fake_conversation_turn()
    )
    monkeypatch.setattr(
        "app.services.speech_service.synthesize_speech", lambda text: b"RIFF....WAVEfake"
    )

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/api/v1/speech/turns",
        files={"audio": ("clip.webm", b"fake-audio-bytes", "audio/webm")},
        headers=headers,
    )
    assert first.status_code == 200
    body = first.json()
    assert body["user_turn"]["text"] == "Ich habe gestern ins Kino gegangen."
    assert body["user_turn"]["grammar_score"] == 70
    assert body["user_turn"]["vocabulary_score"] == 85
    assert body["assistant_turn"]["text"] == "Welchen Film hast du gesehen?"
    assert body["assistant_turn"]["grammar_score"] is None
    conversation_id = body["conversation_id"]

    # Follow-up turn in the same conversation.
    second = await client.post(
        "/api/v1/speech/turns",
        data={"conversation_id": conversation_id},
        files={"audio": ("clip.webm", b"fake-audio-bytes", "audio/webm")},
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id

    thread = await client.get(f"/api/v1/speech/conversations/{conversation_id}", headers=headers)
    assert thread.status_code == 200
    turns = thread.json()["turns"]
    assert [t["role"] for t in turns] == ["user", "assistant", "user", "assistant"]

    summaries = await client.get("/api/v1/speech/conversations", headers=headers)
    assert summaries.status_code == 200
    assert len(summaries.json()) == 1
    assert summaries.json()[0]["turn_count"] == 4

    audio_response = await client.get(
        f"/api/v1/speech/turns/{turns[1]['id']}/audio", headers=headers
    )
    assert audio_response.status_code == 200
    assert audio_response.content == b"RIFF....WAVEfake"


async def test_cannot_access_another_users_speech_conversation(client, user_payload, monkeypatch):
    monkeypatch.setattr(
        "app.services.speech_service.transcribe_audio", lambda audio_bytes: "Hallo"
    )
    monkeypatch.setattr(
        "app.services.speech_service.run_conversation_turn", _fake_conversation_turn()
    )
    monkeypatch.setattr(
        "app.services.speech_service.synthesize_speech", lambda text: b"RIFF....WAVEfake"
    )

    token_a = await _register_and_login(client, user_payload)
    created = await client.post(
        "/api/v1/speech/turns",
        files={"audio": ("clip.webm", b"fake-audio-bytes", "audio/webm")},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    conversation_id = created.json()["conversation_id"]

    other_user = {
        "email": "other-speaker@example.com",
        "password": "supersecret123",
        "full_name": "Other User",
    }
    token_b = await _register_and_login(client, other_user)

    response = await client.get(
        f"/api/v1/speech/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404

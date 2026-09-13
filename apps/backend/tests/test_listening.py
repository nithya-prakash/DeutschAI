"""Listening comprehension endpoint tests — mirrors tests/test_reading.py,
plus audio delivery. `synthesize_speech` is monkeypatched so no real Piper
binary/model download happens in CI, same convention as tests/test_speech.py."""
import uuid

from app.models.listening_script import ListeningScript


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_listening_requires_auth(client):
    response = await client.get("/api/v1/listening/scripts/random")
    assert response.status_code == 401


async def test_get_random_script_never_leaks_the_transcript(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/listening/scripts/random", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["question"]
    assert len(body["options"]) == 4
    assert "script_text" not in body
    assert "audio_object_key" not in body
    assert "correct_option_index" not in body


async def test_script_audio_synthesizes_and_caches_on_first_request(
    client, user_payload, monkeypatch
):
    monkeypatch.setattr(
        "app.services.listening_service.synthesize_speech", lambda text: b"RIFF....WAVEfake"
    )

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    script = (await client.get("/api/v1/listening/scripts/random", headers=headers)).json()

    response = await client.get(
        f"/api/v1/listening/scripts/{script['id']}/audio", headers=headers
    )
    assert response.status_code == 200
    assert response.content == b"RIFF....WAVEfake"

    # Second request hits the now-cached object key — no re-synthesis needed,
    # verified by monkeypatching synthesize_speech to raise if called again.
    monkeypatch.setattr(
        "app.services.listening_service.synthesize_speech",
        lambda text: (_ for _ in ()).throw(AssertionError("should not re-synthesize")),
    )
    cached_response = await client.get(
        f"/api/v1/listening/scripts/{script['id']}/audio", headers=headers
    )
    assert cached_response.status_code == 200
    assert cached_response.content == b"RIFF....WAVEfake"


async def test_correct_answer_does_not_record_a_mistake(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    script = (await client.get("/api/v1/listening/scripts/random", headers=headers)).json()
    db_script = await db_session.get(ListeningScript, uuid.UUID(script["id"]))

    response = await client.post(
        "/api/v1/listening/attempts",
        json={"script_id": script["id"], "selected_option_index": db_script.correct_option_index},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_correct"] is True

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert memories == []


async def test_wrong_answer_records_a_mistake_memory(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    script = (await client.get("/api/v1/listening/scripts/random", headers=headers)).json()
    db_script = await db_session.get(ListeningScript, uuid.UUID(script["id"]))
    wrong_index = next(i for i in range(4) if i != db_script.correct_option_index)

    response = await client.post(
        "/api/v1/listening/attempts",
        json={"script_id": script["id"], "selected_option_index": wrong_index},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_correct"] is False

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert len(memories) == 1
    assert memories[0]["memory_type"] == "mistake"


async def test_attempt_on_unknown_script_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/listening/attempts",
        json={"script_id": "00000000-0000-0000-0000-000000000000", "selected_option_index": 0},
        headers=headers,
    )
    assert response.status_code == 404

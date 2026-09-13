"""Reading comprehension endpoint tests — mirrors tests/test_quizzes.py, but
since multiple passages are seeded per CEFR level (unlike quiz's one
question per topic), the correct answer is peeked from the DB via
`db_session` rather than hardcoded."""
import uuid

from app.models.reading_passage import ReadingPassage


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_reading_requires_auth(client):
    response = await client.get("/api/v1/reading/passages/random")
    assert response.status_code == 401


async def test_get_random_passage_does_not_leak_the_answer(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reading/passages/random", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["passage_text"]
    assert body["question"]
    assert len(body["options"]) == 4
    assert "correct_option_index" not in body
    assert "explanation" not in body


async def test_correct_answer_does_not_record_a_mistake(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    passage = (await client.get("/api/v1/reading/passages/random", headers=headers)).json()
    db_passage = await db_session.get(ReadingPassage, uuid.UUID(passage["id"]))

    response = await client.post(
        "/api/v1/reading/attempts",
        json={
            "passage_id": passage["id"],
            "selected_option_index": db_passage.correct_option_index,
        },
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_correct"] is True
    assert body["explanation"]

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert memories == []


async def test_wrong_answer_records_a_mistake_memory(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    passage = (await client.get("/api/v1/reading/passages/random", headers=headers)).json()
    db_passage = await db_session.get(ReadingPassage, uuid.UUID(passage["id"]))
    wrong_index = next(i for i in range(4) if i != db_passage.correct_option_index)

    response = await client.post(
        "/api/v1/reading/attempts",
        json={"passage_id": passage["id"], "selected_option_index": wrong_index},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_correct"] is False

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert len(memories) == 1
    assert memories[0]["memory_type"] == "mistake"


async def test_attempt_on_unknown_passage_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/reading/attempts",
        json={"passage_id": "00000000-0000-0000-0000-000000000000", "selected_option_index": 0},
        headers=headers,
    )
    assert response.status_code == 404

async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def _get_topic_id(client, headers, name: str) -> str:
    topics = (await client.get("/api/v1/topics", headers=headers)).json()
    return next(t["id"] for t in topics if t["name"] == name)


async def test_quizzes_require_auth(client):
    response = await client.get(
        "/api/v1/quizzes/topics/00000000-0000-0000-0000-000000000000/question"
    )
    assert response.status_code == 401


async def test_get_question_does_not_leak_the_answer(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")

    response = await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["topic_name"] == "Negation (nicht/kein)"
    assert len(body["options"]) == 4
    assert "correct_option_index" not in body
    assert "explanation" not in body


async def test_unknown_topic_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(
        "/api/v1/quizzes/topics/00000000-0000-0000-0000-000000000000/question", headers=headers
    )
    assert response.status_code == 404


async def test_correct_answer_does_not_record_a_mistake(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)
    ).json()

    # The Negation question's correct index is 1 ("Ich habe keine Zeit.").
    response = await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 1},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_correct"] is True
    assert body["correct_option_index"] == 1
    assert body["explanation"]

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert memories == []


async def test_wrong_answer_records_a_mistake_memory(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)
    ).json()

    response = await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 0},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_correct"] is False

    memories = (await client.get("/api/v1/memory", headers=headers)).json()
    assert len(memories) == 1
    assert memories[0]["memory_type"] == "mistake"
    assert memories[0]["related_topic_name"] == "Negation (nicht/kein)"


async def test_attempt_on_unknown_question_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": "00000000-0000-0000-0000-000000000000", "selected_option_index": 0},
        headers=headers,
    )
    assert response.status_code == 404

async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_memory_requires_auth(client):
    response = await client.get("/api/v1/memory")
    assert response.status_code == 401


async def test_new_user_has_no_memories(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.get(
        "/api/v1/memory", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_memories_are_per_user(client, user_payload):
    token_a = await _register_and_login(client, user_payload)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topics = (await client.get("/api/v1/topics", headers=headers_a)).json()
    topic_id = next(t["id"] for t in topics if t["name"] == "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers_a)
    ).json()
    await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 0},
        headers=headers_a,
    )

    other_user = {
        "email": "other-memory@example.com",
        "password": "supersecret123",
        "full_name": "Other User",
    }
    token_b = await _register_and_login(client, other_user)
    response_b = await client.get(
        "/api/v1/memory", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response_b.json() == []

    response_a = await client.get("/api/v1/memory", headers=headers_a)
    assert len(response_a.json()) == 1

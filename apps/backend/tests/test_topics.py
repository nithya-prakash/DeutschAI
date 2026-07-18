async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_topics_requires_auth(client):
    response = await client.get("/api/v1/topics")
    assert response.status_code == 401


async def test_new_user_sees_all_topics_not_started(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/topics", headers=headers)

    assert response.status_code == 200
    topics = response.json()
    # Seeded via migration: 16 grammar + 10 everyday topics.
    assert len(topics) == 26
    assert all(t["status"] == "not_started" for t in topics)
    categories = {t["category"] for t in topics}
    assert categories == {"grammar", "everyday_topic"}


async def test_update_progress_persists(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    topics = (await client.get("/api/v1/topics", headers=headers)).json()
    topic_id = topics[0]["id"]

    update_response = await client.patch(
        f"/api/v1/topics/{topic_id}/progress", json={"status": "mastered"}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "mastered"

    refreshed = (await client.get("/api/v1/topics", headers=headers)).json()
    updated_topic = next(t for t in refreshed if t["id"] == topic_id)
    assert updated_topic["status"] == "mastered"
    # Everything else stays untouched.
    assert sum(1 for t in refreshed if t["status"] == "mastered") == 1


async def test_update_unknown_topic_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/api/v1/topics/00000000-0000-0000-0000-000000000000/progress",
        json={"status": "mastered"},
        headers=headers,
    )
    assert response.status_code == 404


async def test_progress_is_per_user(client, user_payload):
    token_a = await _register_and_login(client, user_payload)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    topics = (await client.get("/api/v1/topics", headers=headers_a)).json()
    topic_id = topics[0]["id"]
    await client.patch(
        f"/api/v1/topics/{topic_id}/progress",
        json={"status": "mastered"},
        headers=headers_a,
    )

    other_user = {
        "email": "other@example.com",
        "password": "supersecret123",
        "full_name": "Other User",
    }
    token_b = await _register_and_login(client, other_user)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    topics_b = (await client.get("/api/v1/topics", headers=headers_b)).json()
    topic_b = next(t for t in topics_b if t["id"] == topic_id)
    assert topic_b["status"] == "not_started"

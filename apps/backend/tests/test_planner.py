async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_planner_requires_auth(client):
    response = await client.get("/api/v1/planner/today")
    assert response.status_code == 401


async def test_plan_blocks_sum_to_available_minutes(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/planner/today?available_minutes=45", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available_minutes"] == 45
    assert sum(block["minutes"] for block in body["blocks"]) == 45
    activities = {block["activity"] for block in body["blocks"]}
    assert activities == {"vocab", "grammar", "listening", "speaking"}


async def test_new_user_has_all_topics_as_weak(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/planner/today", headers=headers)
    assert response.json()["weak_topic_count"] == 26


async def test_mastering_topics_reduces_weak_topic_count(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    topics = (await client.get("/api/v1/topics", headers=headers)).json()
    await client.patch(
        f"/api/v1/topics/{topics[0]['id']}/progress", json={"status": "mastered"}, headers=headers
    )

    response = await client.get("/api/v1/planner/today", headers=headers)
    assert response.json()["weak_topic_count"] == 25


async def test_repeated_calls_are_served_from_cache(client, user_payload, _fake_redis):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.get("/api/v1/planner/today?available_minutes=30", headers=headers)
    assert len(_fake_redis._store) == 1

    # Master a topic — if the second call recomputed instead of hitting the
    # cache, weak_topic_count would drop from 26 to 25.
    topics = (await client.get("/api/v1/topics", headers=headers)).json()
    await client.patch(
        f"/api/v1/topics/{topics[0]['id']}/progress", json={"status": "mastered"}, headers=headers
    )

    second = await client.get("/api/v1/planner/today?available_minutes=30", headers=headers)
    assert second.json() == first.json()


async def test_different_available_minutes_are_cached_separately(client, user_payload, _fake_redis):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    await client.get("/api/v1/planner/today?available_minutes=30", headers=headers)
    await client.get("/api/v1/planner/today?available_minutes=60", headers=headers)

    assert len(_fake_redis._store) == 2

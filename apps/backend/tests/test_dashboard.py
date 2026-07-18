async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_summary_requires_auth(client):
    response = await client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401


async def test_new_user_has_zeroed_summary(client, user_payload):
    token = await _register_and_login(client, user_payload)

    response = await client.get(
        "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_streak_days"] == 0
    assert body["total_study_minutes"] == 0
    assert len(body["last_12_weeks"]) == 12 * 7
    assert len(body["locked_insights"]) > 0


async def test_logging_a_session_updates_streak_and_minutes(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    log_response = await client.post(
        "/api/v1/dashboard/study-sessions",
        json={"duration_minutes": 45, "note": "reviewed Akkusativ"},
        headers=headers,
    )
    assert log_response.status_code == 201
    assert log_response.json()["duration_minutes"] == 45

    summary = await client.get("/api/v1/dashboard/summary", headers=headers)
    body = summary.json()
    assert body["current_streak_days"] == 1
    assert body["longest_streak_days"] == 1
    assert body["total_study_minutes"] == 45
    assert body["weekly_study_minutes"] == 45


async def test_two_sessions_same_day_accumulate_minutes(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/dashboard/study-sessions", json={"duration_minutes": 20}, headers=headers
    )
    await client.post(
        "/api/v1/dashboard/study-sessions", json={"duration_minutes": 25}, headers=headers
    )

    summary = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert summary.json()["total_study_minutes"] == 45
    assert summary.json()["current_streak_days"] == 1

"""Recommendation Engine endpoint tests."""


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


async def test_recommendations_requires_auth(client):
    response = await client.get("/api/v1/recommendations")
    assert response.status_code == 401


async def test_new_user_has_no_recommendations(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.get(
        "/api/v1/recommendations", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"vocab": [], "topics": []}


async def test_reviewed_vocab_appears_in_recommendations(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    word = (
        await client.post(
            "/api/v1/vocabulary",
            json={"german": "das Haus", "english": "the house"},
            headers=headers,
        )
    ).json()
    # Unreviewed words aren't recommendable yet (no forgetting-curve signal).
    unreviewed = (await client.get("/api/v1/recommendations", headers=headers)).json()
    assert unreviewed["vocab"] == []

    await client.post(
        f"/api/v1/vocabulary/{word['id']}/review", json={"quality": 4}, headers=headers
    )

    response = (await client.get("/api/v1/recommendations", headers=headers)).json()
    assert len(response["vocab"]) == 1
    assert response["vocab"][0]["german"] == "das Haus"
    assert 0.0 <= response["vocab"][0]["retention_probability"] <= 1.0
    assert response["vocab"][0]["reason"]


async def test_topic_with_mistakes_appears_in_recommendations(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)
    ).json()

    await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 0},  # wrong
        headers=headers,
    )

    response = (await client.get("/api/v1/recommendations", headers=headers)).json()
    assert len(response["topics"]) == 1
    assert response["topics"][0]["topic_name"] == "Negation (nicht/kein)"
    assert "1 recorded mistake" in response["topics"][0]["reason"]


async def test_mastered_topic_is_not_recommended_even_with_mistakes(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)
    ).json()
    await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 0},
        headers=headers,
    )

    await client.patch(
        f"/api/v1/topics/{topic_id}/progress", json={"status": "mastered"}, headers=headers
    )

    response = (await client.get("/api/v1/recommendations", headers=headers)).json()
    assert response["topics"] == []

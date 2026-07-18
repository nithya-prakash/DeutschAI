async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_vocabulary_requires_auth(client):
    response = await client.get("/api/v1/vocabulary")
    assert response.status_code == 401


async def test_add_word_is_due_immediately(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/vocabulary",
        json={
            "german": "das Haus",
            "english": "the house",
            "example_sentence": "Das Haus ist groß.",
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["german"] == "das Haus"
    assert body["is_due"] is True
    assert body["repetitions"] == 0


async def test_list_is_sorted_by_next_due_date(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/vocabulary", json={"german": "eins", "english": "one"}, headers=headers
    )
    await client.post(
        "/api/v1/vocabulary", json={"german": "zwei", "english": "two"}, headers=headers
    )

    response = await client.get("/api/v1/vocabulary", headers=headers)
    words = response.json()
    assert len(words) == 2
    assert [w["german"] for w in words] == ["eins", "zwei"]


async def test_good_review_advances_due_date_and_clears_due_flag(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    add_response = await client.post(
        "/api/v1/vocabulary", json={"german": "brauchen", "english": "to need"}, headers=headers
    )
    item_id = add_response.json()["id"]

    review_response = await client.post(
        f"/api/v1/vocabulary/{item_id}/review", json={"quality": 4}, headers=headers
    )

    assert review_response.status_code == 200
    body = review_response.json()
    assert body["repetitions"] == 1
    assert body["is_due"] is False


async def test_failed_review_resets_repetitions(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    add_response = await client.post(
        "/api/v1/vocabulary",
        json={"german": "der Termin", "english": "the appointment"},
        headers=headers,
    )
    item_id = add_response.json()["id"]

    await client.post(
        f"/api/v1/vocabulary/{item_id}/review", json={"quality": 4}, headers=headers
    )
    review_response = await client.post(
        f"/api/v1/vocabulary/{item_id}/review", json={"quality": 1}, headers=headers
    )

    body = review_response.json()
    assert body["repetitions"] == 0
    # SM-2 schedules even a failed review a day out (not same-day) — see
    # app/services/spaced_repetition.py.
    assert body["is_due"] is False


async def test_review_nonexistent_word_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/vocabulary/00000000-0000-0000-0000-000000000000/review",
        json={"quality": 4},
        headers=headers,
    )
    assert response.status_code == 404


async def test_delete_removes_word(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    add_response = await client.post(
        "/api/v1/vocabulary", json={"german": "löschen", "english": "to delete"}, headers=headers
    )
    item_id = add_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/vocabulary/{item_id}", headers=headers)
    assert delete_response.status_code == 204

    list_response = await client.get("/api/v1/vocabulary", headers=headers)
    assert list_response.json() == []


async def test_cannot_review_another_users_word(client, user_payload):
    token_a = await _register_and_login(client, user_payload)
    add_response = await client.post(
        "/api/v1/vocabulary",
        json={"german": "geheim", "english": "secret"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    item_id = add_response.json()["id"]

    other_user = {
        "email": "other@example.com",
        "password": "supersecret123",
        "full_name": "Other User",
    }
    token_b = await _register_and_login(client, other_user)

    response = await client.post(
        f"/api/v1/vocabulary/{item_id}/review",
        json={"quality": 4},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404

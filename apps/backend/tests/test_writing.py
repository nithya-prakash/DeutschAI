"""Writing exercise endpoint tests — mirrors tests/test_speech.py's pattern
for an LLM-graded feature: `run_writing_grading` is monkeypatched for the
happy path, plus one test that exercises the real, unconfigured LLM path
and expects the honest 503."""


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_writing_requires_auth(client):
    response = await client.get("/api/v1/writing/prompts/random")
    assert response.status_code == 401


async def test_get_random_prompt(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/writing/prompts/random", headers=headers)

    assert response.status_code == 200
    assert response.json()["prompt_text"]


async def test_submit_writing_without_api_key_returns_503(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    prompt = (await client.get("/api/v1/writing/prompts/random", headers=headers)).json()

    response = await client.post(
        "/api/v1/writing/submissions",
        json={"prompt_id": prompt["id"], "submitted_text": "Ich heiße Ada."},
        headers=headers,
    )

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_submit_writing_persists_scores_and_feedback(client, user_payload, monkeypatch):
    monkeypatch.setattr(
        "app.services.writing_service.run_writing_grading",
        lambda prompt_text, submitted_text, cefr_level: {
            "grammar_score": 75,
            "vocabulary_score": 65,
            "task_completion_score": 85,
            "feedback": "Clear structure, watch your verb endings.",
            "input_tokens": 40,
            "output_tokens": 30,
        },
    )

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    prompt = (await client.get("/api/v1/writing/prompts/random", headers=headers)).json()

    response = await client.post(
        "/api/v1/writing/submissions",
        json={"prompt_id": prompt["id"], "submitted_text": "Ich heiße Ada und wohne in Berlin."},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["grammar_score"] == 75
    assert body["vocabulary_score"] == 65
    assert body["task_completion_score"] == 85
    assert "verb endings" in body["feedback"]


async def test_submit_to_unknown_prompt_returns_404(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/writing/submissions",
        json={
            "prompt_id": "00000000-0000-0000-0000-000000000000",
            "submitted_text": "Hallo.",
        },
        headers=headers,
    )
    assert response.status_code == 404


async def test_submit_writing_rejects_empty_text(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    prompt = (await client.get("/api/v1/writing/prompts/random", headers=headers)).json()

    response = await client.post(
        "/api/v1/writing/submissions",
        json={"prompt_id": prompt["id"], "submitted_text": ""},
        headers=headers,
    )
    assert response.status_code == 422

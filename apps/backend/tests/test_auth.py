async def test_register_creates_user(client, user_payload):
    response = await client.post("/api/v1/auth/register", json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == user_payload["email"]
    assert body["cefr_level"] == "A1"
    assert "hashed_password" not in body


async def test_register_duplicate_email_rejected(client, user_payload):
    await client.post("/api/v1/auth/register", json=user_payload)
    response = await client.post("/api/v1/auth/register", json=user_payload)

    assert response.status_code == 409


async def test_register_rejects_short_password(client, user_payload):
    user_payload["password"] = "short"
    response = await client.post("/api/v1/auth/register", json=user_payload)

    assert response.status_code == 422


async def test_login_with_correct_credentials_returns_tokens(client, user_payload):
    await client.post("/api/v1/auth/register", json=user_payload)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


async def test_login_with_wrong_password_rejected(client, user_payload):
    await client.post("/api/v1/auth/register", json=user_payload)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_me_requires_authentication(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_me_returns_current_user(client, user_payload):
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    access_token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == user_payload["email"]


async def test_refresh_issues_new_tokens(client, user_payload):
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert response.json()["access_token"]

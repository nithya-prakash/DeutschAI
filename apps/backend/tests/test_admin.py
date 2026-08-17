"""Admin panel endpoint tests — every route gated on is_superuser."""
from sqlalchemy import select

from app.models.user import User


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def _make_superuser(db_session, email: str) -> None:
    user = (await db_session.execute(select(User).where(User.email == email))).scalar_one()
    user.is_superuser = True
    await db_session.commit()


async def test_admin_endpoints_require_auth(client):
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 401


async def test_regular_user_gets_403(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


async def test_superuser_can_list_users(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert user_payload["email"] in emails
    assert response.json()[0]["is_superuser"] is True


async def test_system_health_reflects_configuration(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get(
        "/api/v1/admin/system-health", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    # No ANTHROPIC_API_KEY/SENTRY_DSN/OTEL_EXPORTER_OTLP_ENDPOINT set in the
    # test environment, so these are correctly reported as not configured.
    assert body["anthropic_configured"] is False
    assert body["sentry_configured"] is False
    assert body["otel_configured"] is False
    service_names = {s["name"] for s in body["services"]}
    assert service_names == {"postgres", "redis", "qdrant", "minio"}
    postgres_status = next(s for s in body["services"] if s["name"] == "postgres")
    assert postgres_status["reachable"] is True


async def test_llm_usage_empty_for_fresh_install(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get(
        "/api/v1/admin/llm-usage", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"by_agent": []}


async def test_llm_usage_reflects_a_real_tutor_call(client, user_payload, db_session, monkeypatch):
    def fake_ask_tutor(question: str, cefr_level: str):
        return {
            "question": question,
            "cefr_level": cefr_level,
            "context_chunks": [],
            "answer": "ok",
            "input_tokens": 100,
            "output_tokens": 40,
        }

    monkeypatch.setattr("app.services.tutor_service.ask_tutor", fake_ask_tutor)

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/tutor/ask", json={"question": "hi"}, headers=headers)
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get("/api/v1/admin/llm-usage", headers=headers)
    assert response.json() == {
        "by_agent": [
            {"agent_name": "tutor", "call_count": 1, "input_tokens": 100, "output_tokens": 40}
        ]
    }


async def test_session_activity_reflects_real_sessions(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/dashboard/study-sessions", json={"duration_minutes": 30}, headers=headers
    )
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get("/api/v1/admin/session-activity", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["sessions_today"] == 1
    assert body["sessions_this_week"] == 1
    assert body["active_users_this_week"] == 1


async def test_error_logs_empty_by_default(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    await _make_superuser(db_session, user_payload["email"])

    response = await client.get(
        "/api/v1/admin/error-logs", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []

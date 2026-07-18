"""Global exception handler tests — Phase 6 local error-log persistence
(app/main.py's `_unhandled_exception_handler`).

Two of these tests build their own client with `raise_app_exceptions=False`
rather than using the shared `client` fixture — httpx's `ASGITransport`
re-raises unhandled server exceptions into the test process by default (so
a genuine bug elsewhere fails its test loudly), which is exactly the
behavior these two need to turn off in order to observe the *handled* 500
response instead of the raw exception.
"""
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _register_and_login(client, user_payload) -> str:
    await client.post("/api/v1/auth/register", json=user_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    return login.json()["access_token"]


async def test_unhandled_exception_returns_honest_500(client, user_payload, monkeypatch):
    def _boom(self, user_id):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr("app.services.dashboard_service.DashboardService.get_summary", _boom)
    token = await _register_and_login(client, user_payload)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as tolerant_client:
        response = await tolerant_client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


async def test_unhandled_exception_is_logged_locally(
    client, user_payload, db_session, monkeypatch
):
    from sqlalchemy import select

    from app.models.error_log_entry import ErrorLogEntry

    def _boom(self, user_id):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr("app.services.dashboard_service.DashboardService.get_summary", _boom)
    token = await _register_and_login(client, user_payload)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as tolerant_client:
        await tolerant_client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

    entries = (await db_session.execute(select(ErrorLogEntry))).scalars().all()
    assert len(entries) == 1
    assert entries[0].method == "GET"
    assert entries[0].path == "/api/v1/dashboard/summary"
    assert entries[0].exception_type == "RuntimeError"
    assert entries[0].message == "simulated failure"


async def test_http_exceptions_are_not_swallowed_into_a_500(client, user_payload):
    token = await _register_and_login(client, user_payload)
    response = await client.get(
        "/api/v1/tutor/conversations/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

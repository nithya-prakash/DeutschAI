import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models.grammar_topic import GrammarTopic
from app.models.study_session import StudySession
from app.models.user_topic_progress import TopicStatus, UserTopicProgress


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

    # Phase 5: no data yet anywhere means honest gaps, not fabricated numbers.
    assert body["skill_scores"] == {"grammar": None, "vocabulary": None, "speaking": None}
    assert body["weakest_topics"] == []
    assert body["strongest_topics"] == []
    assert body["predicted_milestone"] is None
    assert body["consistency_score"] is None
    assert body["best_study_day"] is None
    assert body["vocab_at_risk_count"] == 0
    assert body["motivation_message"] is None


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


# --- Phase 5: skill scores, topic rankings, forecasting, habit intelligence ---


async def _get_topic_id(client, headers, name: str) -> str:
    topics = (await client.get("/api/v1/topics", headers=headers)).json()
    return next(t["id"] for t in topics if t["name"] == name)


async def test_wrong_quiz_answer_produces_grammar_score_and_weakest_topic(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = await _get_topic_id(client, headers, "Negation (nicht/kein)")
    question = (
        await client.get(f"/api/v1/quizzes/topics/{topic_id}/question", headers=headers)
    ).json()

    # Deliberately wrong (correct index is 1) so a mistake is recorded.
    await client.post(
        "/api/v1/quizzes/attempts",
        json={"question_id": question["id"], "selected_option_index": 0},
        headers=headers,
    )

    summary = (await client.get("/api/v1/dashboard/summary", headers=headers)).json()
    assert summary["skill_scores"]["grammar"] == 0.0
    assert len(summary["weakest_topics"]) == 1
    assert summary["weakest_topics"][0]["topic_name"] == "Negation (nicht/kein)"
    assert summary["weakest_topics"][0]["mistake_count"] == 1


async def test_reviewed_vocabulary_produces_vocabulary_skill_score(client, user_payload):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    word = (
        await client.post(
            "/api/v1/vocabulary",
            json={"german": "das Haus", "english": "the house"},
            headers=headers,
        )
    ).json()
    await client.post(
        f"/api/v1/vocabulary/{word['id']}/review", json={"quality": 4}, headers=headers
    )

    summary = (await client.get("/api/v1/dashboard/summary", headers=headers)).json()
    assert summary["skill_scores"]["vocabulary"] is not None
    assert 0.0 < summary["skill_scores"]["vocabulary"] <= 100.0
    # Reviewed a moment ago — essentially full retention, not at risk.
    assert summary["vocab_at_risk_count"] == 0


async def test_scored_speech_turn_produces_speaking_score(client, user_payload, monkeypatch):
    monkeypatch.setattr(
        "app.services.speech_service.transcribe_audio", lambda audio_bytes: "Hallo!"
    )
    monkeypatch.setattr(
        "app.services.speech_service.run_conversation_turn",
        lambda user_utterance, cefr_level, history: {
            "reply": "Hallo! Wie geht's?",
            "grammar_score": 80,
            "vocabulary_score": 90,
            "feedback": "Good start.",
            "input_tokens": 25,
            "output_tokens": 15,
        },
    )
    monkeypatch.setattr(
        "app.services.speech_service.synthesize_speech", lambda text: b"RIFF....WAVEfake"
    )

    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/speech/turns",
        files={"audio": ("clip.webm", b"fake-audio-bytes", "audio/webm")},
        headers=headers,
    )

    summary = (await client.get("/api/v1/dashboard/summary", headers=headers)).json()
    assert summary["skill_scores"]["speaking"] == 85.0


async def test_predicted_milestone_appears_with_real_mastery_history(
    client, user_payload, db_session
):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    me = (await client.get("/api/v1/users/me", headers=headers)).json()
    user_id = uuid.UUID(me["id"])

    topics = (await db_session.execute(select(GrammarTopic).limit(2))).scalars().all()
    now = datetime.now(UTC)
    db_session.add(
        UserTopicProgress(
            user_id=user_id,
            topic_id=topics[0].id,
            status=TopicStatus.MASTERED,
            updated_at=now - timedelta(days=20),
        )
    )
    db_session.add(
        UserTopicProgress(
            user_id=user_id,
            topic_id=topics[1].id,
            status=TopicStatus.MASTERED,
            updated_at=now - timedelta(days=10),
        )
    )
    await db_session.commit()

    summary = (await client.get("/api/v1/dashboard/summary", headers=headers)).json()
    assert summary["predicted_milestone"] is not None
    assert summary["predicted_milestone"]["topics_remaining"] == 24


async def test_motivation_message_appears_after_a_gap(client, user_payload, db_session):
    token = await _register_and_login(client, user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/dashboard/study-sessions", json={"duration_minutes": 30}, headers=headers
    )

    # Back-date the just-logged session to simulate a multi-day gap.
    session_row = (await db_session.execute(select(StudySession))).scalars().first()
    session_row.studied_on = datetime.now(UTC) - timedelta(days=5)
    await db_session.commit()

    summary = (await client.get("/api/v1/dashboard/summary", headers=headers)).json()
    assert summary["motivation_message"] is not None
    assert summary["motivation_message"]["suggested_minutes"] < 30

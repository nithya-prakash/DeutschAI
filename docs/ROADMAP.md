# Roadmap

The original product brief for DeutschAI describes a full platform: multiple
LangGraph agents (Tutor, Planner, Assessment, Memory, Motivation), a RAG
knowledge base over Qdrant, a Whisper-based speech/conversation engine,
traditional-ML components (forgetting curve, habit prediction, recommendation
ranking), a full analytics dashboard, an admin panel, and a production
observability/CI stack. That's a multi-month build. This roadmap maps every
piece of that brief to the phase it lands in, so "planned" and "shipped" stay
distinguishable.

## Phase 1 — Done ✅

Core authentication, user profile, database layer, Docker setup.

- [x] FastAPI backend, clean architecture (api / services / repositories / models)
- [x] JWT auth (register, login, refresh)
- [x] User model (email, name, CEFR level, native/target language)
- [x] `StudySession` model + a dashboard that computes real streak/minutes from it
- [x] Alembic migrations, async SQLAlchemy against Postgres
- [x] Next.js frontend: auth pages, protected dashboard shell, dark mode
- [x] Full local stack via `docker compose up` (Postgres, Redis, Qdrant, MinIO,
      backend, frontend, nginx — Qdrant/MinIO provisioned but idle until Phase 3/4)
- [x] Pytest suite (14 tests) against in-memory SQLite; Vitest unit tests on the frontend

## Phase 2 — Learning Engine — Done ✅

- [x] `vocabulary_items`, `grammar_topics`, `user_topic_progress` tables
- [x] CEFR A1 roadmap content seeded via migration (16 grammar topics + the
      10 real Goethe-Zertifikat A1 Sprechen topics), single source of truth
      in `app/domain/curriculum_reference.py`
- [x] Intelligent spaced repetition: SM-2 (`app/services/spaced_repetition.py`)
      — ease factor + review history drive the next interval, replacing fixed
      1/3/7/14/30/60-day steps. A failed review resets progress rather than
      just repeating the same step
- [x] Planner Agent (LangGraph): `app/ai/planner_agent.py` — a 3-node graph
      (assess → allocate → render) that turns available minutes + due-vocab
      count + weak-topic count into a time-boxed daily plan. Deterministic
      Python nodes, no LLM call yet — see the module docstring for why, and
      where Phase 3 would add an LLM-backed node
- [x] Redis actually in use: the planner result is cached per user/day/duration
      (`app/services/planner_service.py`) — background job queue (rq/arq)
      still pending, deferred until there's an actual async job to run
- [x] Frontend: `/vocabulary` (Again/Hard/Good/Easy review), `/curriculum`
      (click-to-cycle status + progress bars), `/planner` (adjustable minutes,
      color-coded plan blocks); dashboard gained two more real stat tiles
      (vocab due, topics mastered)
- [x] 40 passing pytest tests (26 new: SM-2 unit tests + vocabulary/topics/
      planner API tests, the latter using a fake in-memory Redis)

## Phase 3 — AI Tutor, RAG, Memory, Quizzes — Done ✅

- [x] Knowledge base: 16 original A1 grammar reference notes
      (`app/ai/rag/knowledge_base/*.md`), chunked and embedded with `fastembed`
      (local ONNX model, no torch, no embedding API key) into Qdrant
      (`app/ai/rag/ingest.py` — idempotent, deterministic point IDs)
- [x] Retriever + Tutor Agent (`app/ai/tutor_agent.py`): a 2-node LangGraph
      graph (retrieve → generate) using Claude (`langchain-anthropic`) —
      unlike the Planner Agent, this one genuinely needs generation, so it
      requires `ANTHROPIC_API_KEY`. Fails loudly with a clear HTTP 503 if
      unset rather than faking a response; verified this actually happens
      (checked no orphaned DB rows get left behind either)
- [x] Assessment Agent (`app/services/assessment_service.py`): 16 seeded
      multiple-choice questions (one per grammar topic), graded by index
      comparison — deliberately no LLM, since grading MCQ needs none
- [x] Memory Agent (`app/services/memory_service.py`): `ai_memories` table —
      a wrong quiz answer is recorded as a `mistake` memory tied to its topic,
      surfaced as a "Recent mistakes" feed on the dashboard. Deeper feedback
      into the Planner Agent's weak-topic weighting is a natural Phase 5
      extension once there's usage data to tune it against, not built yet
- [x] `conversations` + `conversation_messages` tables: the Tutor Agent's chat
      history actually persists, with ownership checks (one user can't read
      another's conversation)
- [x] Frontend: `/tutor` (chat UI, gracefully explains the 503 instead of a
      generic error), `/quiz` (topic picker → MCQ → explanation), a
      "Recent mistakes" card on the dashboard
- [x] 65 passing pytest tests (25 new: RAG ingestion/retrieval against an
      in-memory Qdrant with real embeddings, Tutor Agent graph tests against
      a fake chat model, quiz/memory/ownership tests)

## Phase 4 — Speech Engine, Conversation Mode — Done ✅

- [x] Whisper STT: `app/ai/speech/stt.py` runs `faster-whisper` locally
      (CPU, int8, no API key) — model downloaded once and cached in
      `.whisper_cache/`, same lazy-cache shape as fastembed's embedding model
- [x] TTS: `app/ai/speech/tts.py` shells out to Piper's official CLI binary
      (not the `piper-tts` Python package — its native `piper-phonemize`
      dependency has no Linux ARM64 wheel, which this backend's Docker image
      needs on Apple Silicon). Binary + `de_DE-thorsten-medium` voice
      downloaded once and cached in `.piper_cache/`
- [x] MinIO now actually in use: `app/infrastructure/object_store/` stores
      both the learner's uploaded recordings and the synthesized replies,
      streamed back through an authenticated backend endpoint
      (`GET /speech/turns/{id}/audio`) rather than a public presigned URL
- [x] Conversation Agent (`app/ai/conversation_agent.py`): a 2-node LangGraph
      graph (generate → parse) reusing the Tutor Agent's Claude client/
      `LLMNotConfiguredError` contract. One Claude call per turn continues
      the dialogue *and* scores the learner's grammar/vocabulary
- [x] Pronunciation/fluency are **not** faked — Claude has no audio input, so
      there's no real signal for either yet; the frontend shows them as
      locked (`LockedInsights`) rather than the API inventing a number
- [x] `speech_conversations` / `speech_turns` tables, ownership-checked like
      every other per-user resource
- [x] Frontend: `/conversation` — `MediaRecorder`-based mic capture, turn
      history with inline audio playback and grammar/vocabulary feedback
- [x] 75 passing pytest tests (10 new: Conversation Agent graph tests with a
      fake chat model, STT/TTS wrapper tests with fake underlying
      model/voice objects, turn persistence/ownership/503 endpoint tests
      with a fake in-memory object store)

## Phase 5 — Recommendation Engine, ML, Analytics

- [ ] Content recommendation (grammar/vocab/podcasts/articles) ranked by
      interests + CEFR level + mistake history
- [ ] Habit Intelligence: best study time, skip patterns, consistency score —
      a real behavioral model, not a hardcoded threshold
- [ ] Lightweight traditional-ML components (explicitly *not* LLM calls):
      vocabulary forgetting-probability model, session-skip prediction,
      recommendation ranking, progress forecasting
- [ ] Motivation Agent: streak-recovery messaging, adaptive workload reduction
      after a skip — never a guilt-trip, always "reduce and re-invite"
- [ ] Full analytics dashboard (skill scores, weakest/strongest topics,
      predicted milestone) replacing today's `locked_insights` placeholders

## Phase 6 — Monitoring, CI/CD, Production Hardening

- [ ] GitHub Actions: lint + test + build on every push (a minimal version
      ships in Phase 1 as `.github/workflows/ci.yml`; this phase adds deploy)
- [ ] Prometheus + Grafana dashboards, OpenTelemetry tracing, Sentry
- [ ] Admin panel: users, sessions, LLM token spend, system health, error logs
- [ ] Playwright E2E suite expanded beyond the Phase-1 smoke test
- [ ] Production deployment target (the brief doesn't specify a cloud —
      decide this with the user before building it, since it's a real cost
      and access-control commitment, not just code)

## Explicit non-goals for now

- No fake data, mocked LLM responses, or hardcoded "AI insights" standing in
  for the agents above — the dashboard shows a metric as **locked**, never
  as a plausible-looking number that isn't real.
- No admin panel until there's something real to administer (Phase 6).
- Multi-language support beyond German is an architectural constraint on
  every phase (`target_language` on `User`, no hardcoded "German" in any
  service/repository), not a separate phase — there's nothing to "add later"
  if Phase 1–5 don't hardcode the language.

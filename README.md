# DeutschAI

An AI-powered, adaptive platform for learning German from A1 to C1 — architected so
additional languages (Spanish, French, Japanese, …) can be added later without
reworking the core.

**Status: Phase 6 of 6 — all phases shipped.** This repo ships a real, working
platform — auth, user profiles, a study-streak dashboard, vocabulary spaced
repetition, a curriculum roadmap, a LangGraph daily planner, a RAG-grounded
AI Tutor, a local speech engine with turn-taking Conversation Mode, a
recommendation/analytics engine, and monitoring/CI/CD/an admin panel. See
[`docs/ROADMAP.md`](docs/ROADMAP.md) for exactly what each phase delivered
(including the deliberate scope trims — no chosen production deployment
target, no Prometheus/Grafana, no podcast/article recommendations), and
don't take marketing copy about "AI agents" at face value until it shows up
in that roadmap as shipped.

## What's actually working right now

- Email/password registration and login (JWT access + refresh tokens)
- User profile (name, CEFR level, target language)
- A dashboard that logs real study sessions and computes a real streak,
  longest streak, and weekly/total minutes from them — plus a GitHub-style
  heatmap of the last 12 weeks
- **Vocabulary notebook** (`/vocabulary`) with genuine SM-2 spaced repetition —
  Again/Hard/Good/Easy reviews adjust each word's ease factor and next-due date
- **Curriculum roadmap** (`/curriculum`) — the real Goethe-Zertifikat A1 grammar
  syllabus + Sprechen topic list, click-to-cycle progress per topic
- **Daily planner** (`/planner`) — a LangGraph agent (deterministic nodes, no
  LLM call needed) allocates your available minutes across vocab/grammar/
  listening/speaking based on what's actually due and unmastered, cached in
  Redis per user/day
- **AI Tutor** (`/tutor`) — a RAG-grounded LangGraph agent: retrieves from a
  Qdrant knowledge base (16 original A1 grammar notes, embedded locally with
  `fastembed`, no embedding API key needed) and generates an answer with
  Claude, tailored to your CEFR level. Requires `ANTHROPIC_API_KEY` — without
  it, the endpoint returns a clear, honest "not configured" message instead of
  faking a response, and everything else in the app still works
- **Practice quiz** (`/quiz`) — 16 seeded multiple-choice questions, graded
  deterministically (no LLM). A wrong answer is recorded by the Memory Agent
  and shows up as a "Recent mistakes" card on the dashboard
- **Conversation Mode** (`/conversation`) — record yourself speaking German,
  get a real transcript (`faster-whisper`, local, no API key), a real
  Claude-generated reply from a LangGraph Conversation Agent scoring your
  grammar/vocabulary, and a real synthesized spoken reply (Piper, local, no
  API key) — pronunciation/fluency scoring has no real signal yet, so it's
  shown as explicitly "locked" rather than faked
- **Recommendation Engine & Analytics** (on `/dashboard`) — real grammar/
  vocabulary/speaking skill scores, weakest/strongest topic rankings, a
  progress-forecast milestone, habit-intelligence figures (consistency
  score, best study day), a "recommended focus" list (due vocab + weak
  topics, internal content only — no invented podcasts/articles), and a
  Motivation Agent banner after a study gap. Every number is computed from
  your own real history — no new DB tables were even needed for this
- **Admin panel** (`/admin`, superuser-only) — a real user list, real
  per-service reachability checks (Postgres/Redis/Qdrant/MinIO), real
  session activity across all users, real LLM token counts by agent (empty
  until `ANTHROPIC_API_KEY` is set and calls happen), and a local error log
  fed by a global exception handler. Sentry and OpenTelemetry are wired up
  too, each activating only once its own setting (`SENTRY_DSN`,
  `OTEL_EXPORTER_OTLP_ENDPOINT`) is configured
- CI now builds both Docker images on every push to `main` as a deploy-
  readiness check — it doesn't push anywhere yet; picking a real hosting
  target is a deliberately separate decision
- Dark mode
- The full local dev stack (Postgres, Redis, Qdrant, MinIO, backend, frontend,
  nginx) via one `docker compose up` — MinIO now actually stores the
  recorded/synthesized audio blobs from Conversation Mode

Metrics with no real signal anywhere in the app yet (listening, reading, and
writing scores) are shown on the dashboard as explicitly "locked," not faked
with placeholder numbers.

## Quick start

```bash
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env

docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs (Swagger): http://localhost:8000/api/v1/docs
- Through the nginx reverse proxy: http://localhost

The backend entrypoint waits for Postgres and runs Alembic migrations
automatically on container start — no manual migration step needed for a
fresh clone.

## Repository layout

```
deutschai/
├── apps/
│   ├── backend/          FastAPI + SQLAlchemy (async) + Alembic
│   └── frontend/          Next.js (App Router) + TypeScript + Tailwind + shadcn/ui
├── infra/
│   └── nginx/              Reverse proxy config
├── docs/
│   ├── ARCHITECTURE.md    Clean-architecture layering, DB schema, request flow
│   └── ROADMAP.md          Phase-by-phase plan mapped to the full product vision
├── .github/workflows/     CI (lint + test + build on every push; a deploy
│                          job builds both Docker images but pushes nowhere)
└── docker-compose.yml
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the backend layers
fit together and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full multi-phase
plan (Learning Engine, AI Tutor/RAG, Speech, Recommendations, ML, Monitoring).

## Development

### Backend

```bash
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then point POSTGRES_HOST/REDIS_HOST at localhost
alembic upgrade head
python -m app.ai.rag.ingest  # embeds the knowledge base into Qdrant (needed for /tutor)
uvicorn app.main:app --reload
pytest                  # 65 tests, in-memory SQLite/Qdrant + fake Redis, no external services needed
```

### Frontend

```bash
cd apps/frontend
npm install
cp .env.example .env
npm run dev
npm run test            # Vitest unit tests
npm run test:e2e         # Playwright — requires the full stack running
```

## License

Unlicensed portfolio/demo project.

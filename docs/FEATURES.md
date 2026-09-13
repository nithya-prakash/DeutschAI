# Platform Overview

DeutschAI is an AI-powered, adaptive platform for learning German from A1
toward C1. It combines a spaced-repetition learning engine, a
retrieval-grounded AI tutor, a local speech and conversation practice
engine, and a lightweight machine-learning layer for personalization —
all served through a clean-architecture FastAPI backend and a Next.js
frontend, containerized end to end with Docker.

The system is architected so that additional target languages can be added
without reworking the core: language is a per-user setting
(`target_language` on `User`), never hardcoded into a service or
repository.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for backend layering, the database
schema, and implementation detail on each component below.

## 1. Authentication & User Management

- Stateless JWT authentication (access + refresh tokens, `HS256`)
- User profiles with CEFR level, native language, and target language
- Role-based access via a superuser flag gating the admin panel
- Async SQLAlchemy against PostgreSQL, schema managed with Alembic
  migrations

## 2. Adaptive Learning Engine

- Curriculum tracking against the real Goethe-Zertifikat A1 grammar and
  Sprechen syllabus, with per-user progress state
- A vocabulary notebook driven by genuine SM-2 spaced repetition — review
  quality adjusts each word's ease factor and next-due date, rather than a
  fixed review schedule
- A daily Planner Agent, implemented as a deterministic LangGraph graph,
  that allocates available study time across vocabulary, grammar,
  listening, and speaking based on what's actually due and unmastered,
  with results cached per user/day in Redis
- Reading comprehension exercises — short passages with a comprehension
  question, graded deterministically like the Assessment Agent's quizzes

## 3. RAG Knowledge Base & AI Tutor

- A curated German grammar knowledge base, chunked and embedded locally
  with `fastembed` (an ONNX runtime model, avoiding a GPU/torch dependency)
  and indexed in Qdrant for vector retrieval
- A Tutor Agent — a retrieval-augmented LangGraph graph backed by Claude
  (`langchain-anthropic`) — that grounds its explanations in retrieved
  reference material and tailors them to the learner's CEFR level
- Persisted conversation history with per-user ownership checks
- A deterministic Assessment Agent (multiple-choice quizzes, graded by
  index comparison — no LLM call needed) and a Memory Agent that records
  mistakes and feeds them into topic-strength analytics and recommendations

## 4. Speech & Conversation Engine

- Local speech-to-text via `faster-whisper` (CTranslate2-based, CPU
  inference, no external API dependency)
- Local text-to-speech via Piper, invoked through its native CLI binary
- MinIO-backed object storage for recorded and synthesized audio, served
  back through authenticated, ownership-checked endpoints
- A Conversation Agent — a LangGraph graph backed by Claude — that runs
  turn-taking spoken dialogue practice and scores grammar and vocabulary
  per turn from the transcript, plus pronunciation and fluency scores
  derived from the speech-to-text engine's own decode signal (word-level
  confidence and timing) rather than from Claude, which only ever sees text
- Listening comprehension exercises — short clips synthesized once via the
  local Piper voice and cached, with a comprehension question graded
  deterministically
- A Writing Agent — the same LLM-graded LangGraph shape as the Conversation
  Agent — that grades a submitted response to a prompt on grammar,
  vocabulary, and task completion, with brief feedback

## 5. Machine Learning & Recommendations

- A forgetting-curve retention model (Ebbinghaus-style exponential decay)
  computed from each vocabulary item's spaced-repetition state
- Habit intelligence: a recency-weighted consistency score, a skip-
  probability model blending day-of-week and recent-trend signals, and
  best-study-day detection, all computed from real study-session history
- Progress forecasting via a trend fit over topic-mastery history,
  projecting a completion date
- A Recommendation Agent — a deterministic LangGraph graph — that ranks
  vocabulary and grammar topics for review based on retention risk and
  mistake history
- A Motivation Agent that generates adaptive, encouraging messaging and a
  reduced-workload suggestion after a study gap

## 6. Analytics & Admin

- Real skill scoring (grammar, vocabulary, speaking, reading, listening,
  writing) and weakest/strongest topic rankings, computed from quiz,
  vocabulary, conversation, reading, listening, and writing history
- An admin panel, gated to superuser accounts, covering user management,
  infrastructure health checks (database, cache, vector store, object
  storage), LLM usage metrics, session activity, and an error log

## 7. Testing, CI/CD & Observability

- Backend testing: a Pytest suite of 143 tests covering authentication,
  learning workflows, RAG retrieval, LangGraph agents, the speech
  pipeline, reading/listening/writing exercises, ML components, analytics,
  the admin panel, and error handling
- Frontend testing: Vitest unit tests and a Playwright end-to-end suite
  covering authentication, the dashboard, vocabulary review, the AI tutor,
  and admin access control
- Continuous integration via GitHub Actions: linting, type-checking,
  automated tests, and a container build/deploy-readiness check on every
  push
- Observability integrations for Sentry (error tracking) and OpenTelemetry
  (distributed tracing), both configuration-driven and inert until a
  target is configured

## Technology Stack

**Backend:** FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, Redis,
Qdrant, MinIO, LangGraph, Claude (Anthropic), fastembed, faster-whisper,
Piper TTS

**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, TanStack
Query, Zustand

**Infrastructure & tooling:** Docker / Docker Compose, nginx, GitHub
Actions, Pytest, Vitest, Playwright, OpenTelemetry, Sentry

## Future Work

- Production cloud deployment
- Expanded multilingual support beyond German
- Additional learning content sources (e.g. podcasts, articles)

"""Shared pytest fixtures.

Tests run against an in-memory SQLite database rather than Postgres — the
ORM models use dialect-portable types (`sqlalchemy.Uuid`, `sqlalchemy.Enum`)
specifically so this works. This keeps the unit/integration suite fast and
dependency-free; a real Postgres is still exercised via `docker compose`
in CI/staging.
"""
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use")
os.environ.setdefault("ENVIRONMENT", "test")

from collections.abc import AsyncGenerator  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api.deps import get_object_storage, get_redis  # noqa: E402
from app.domain.curriculum_reference import EVERYDAY_TOPICS, GRAMMAR_TOPICS  # noqa: E402
from app.domain.quiz_reference import QUIZ_QUESTIONS  # noqa: E402
from app.infrastructure.database.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, GrammarTopic, QuizQuestion  # noqa: E402
from app.models.grammar_topic import TopicCategory  # noqa: E402

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


async def _seed_curriculum(conn) -> None:
    """Mirrors the Alembic migration's seed data — the app models here, not
    raw SQL, since this runs against the test engine via `run_sync`."""

    def _insert(sync_conn) -> None:
        session = Session(bind=sync_conn)
        try:
            topics_by_name: dict[str, GrammarTopic] = {}
            for index, name in enumerate(GRAMMAR_TOPICS):
                topic = GrammarTopic(category=TopicCategory.GRAMMAR, name=name, order_index=index)
                session.add(topic)
                topics_by_name[name] = topic
            for index, name in enumerate(EVERYDAY_TOPICS):
                session.add(
                    GrammarTopic(
                        category=TopicCategory.EVERYDAY_TOPIC, name=name, order_index=index
                    )
                )
            session.flush()

            for topic_name, question, options, correct_index, explanation in QUIZ_QUESTIONS:
                session.add(
                    QuizQuestion(
                        topic_id=topics_by_name[topic_name].id,
                        question=question,
                        options=options,
                        correct_option_index=correct_index,
                        explanation=explanation,
                    )
                )
            session.commit()
        finally:
            session.close()

    await conn.run_sync(_insert)


@pytest_asyncio.fixture(autouse=True)
async def _prepare_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _seed_curriculum(conn)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


class FakeRedis:
    """In-memory stand-in for redis.asyncio.Redis — just enough of the API
    (get/set with an ignored expiry) for the planner cache to exercise."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value


@pytest.fixture(autouse=True)
def _fake_redis() -> FakeRedis:
    """Fresh per-test instance, shared across every request within that test
    (so cache-hit behavior is actually exercisable) but never leaking into
    the next test."""
    instance = FakeRedis()
    app.dependency_overrides[get_redis] = lambda: instance
    return instance


class FakeObjectStore:
    """In-memory stand-in for `ObjectStore` — the speech endpoints exercise
    real upload/download logic without a real MinIO."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self._store[key] = data

    def get_object(self, key: str) -> bytes:
        return self._store[key]

    def is_reachable(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def _fake_object_store() -> FakeObjectStore:
    instance = FakeObjectStore()
    app.dependency_overrides[get_object_storage] = lambda: instance
    return instance


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Direct access to the same test database the API uses, for seeding
    state (e.g. back-dated timestamps) that isn't reachable by driving the
    real endpoints alone."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def user_payload() -> dict:
    return {
        "email": "learner@example.com",
        "password": "supersecret123",
        "full_name": "Ada Lovelace",
    }

"""Alembic migration environment.

Runs migrations through the app's async engine (the standard SQLAlchemy 2.0
async-Alembic recipe: sync migration functions executed via `run_sync`
inside the async connection).
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from app.core.config import get_settings
from app.infrastructure.database.session import engine
from app.models import Base  # noqa: F401  (imports all models onto Base.metadata)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()


def run_migrations_offline() -> None:
    context.configure(
        url=str(settings.DATABASE_URI),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable: AsyncEngine = engine
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

"""FastAPI application factory and entrypoint."""
import logging
import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    # Captures unhandled exceptions automatically via Sentry's ASGI/FastAPI
    # integration — independent of the local error-log handler below, which
    # exists so there's an at-a-glance error view with no external dependency.
    import sentry_sdk

    sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)

if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
    # Deliberately skipped entirely (not a no-op exporter) when unset — there's
    # no point instrumenting spans with nowhere real to send them.
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from app.infrastructure.database.session import engine as _db_engine

    _tracer_provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: settings.OTEL_SERVICE_NAME})
    )
    _tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT))
    )
    trace.set_tracer_provider(_tracer_provider)
    SQLAlchemyInstrumentor().instrument(engine=_db_engine.sync_engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("%s starting up in %s mode", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("%s shutting down", settings.PROJECT_NAME)


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Logs (existing logger + Sentry, both independent of this handler) and
    best-effort persists a real `ErrorLogEntry` row — the admin panel's
    local "Error logs" tab reads from this table without depending on
    Sentry's API. The persistence step is defensive: if the exception being
    handled *is* a DB outage, failing to also log it must not crash the
    handler or block returning the 500 response."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)

    try:
        from app.infrastructure.database.session import get_db
        from app.models.error_log_entry import ErrorLogEntry

        # Goes through the same overridable `get_db` the rest of the app
        # uses (rather than the raw session factory directly) so the test
        # suite's DB override applies here too, instead of this silently
        # writing to a different database than the one being tested.
        session_dependency = request.app.dependency_overrides.get(get_db, get_db)
        async for session in session_dependency():
            session.add(
                ErrorLogEntry(
                    method=request.method,
                    path=request.url.path,
                    exception_type=type(exc).__name__,
                    message=str(exc),
                    traceback=traceback.format_exc(),
                )
            )
            await session.commit()
            break
    except Exception:
        logger.exception("Failed to persist error log entry")

    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "DeutschAI backend API: authentication, user profiles, the "
            "study-streak dashboard, vocabulary spaced repetition, the "
            "curriculum roadmap, a LangGraph daily planner, a RAG-grounded "
            "AI Tutor Agent, Conversation Mode, a recommendation/analytics "
            "engine, and observability + an admin panel (needs "
            "ANTHROPIC_API_KEY / SENTRY_DSN / OTEL_EXPORTER_OTLP_ENDPOINT "
            "for the gated pieces)."
        ),
        version="0.6.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, _unhandled_exception_handler)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)

    return app


app = create_app()

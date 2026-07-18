"""FastAPI application factory and entrypoint."""
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("%s starting up in %s mode", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("%s shutting down", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "DeutschAI backend API. Phase 3: authentication, user profiles, "
            "the study-streak dashboard, vocabulary spaced repetition, the "
            "curriculum roadmap, a LangGraph daily planner, and a "
            "RAG-grounded AI Tutor Agent (needs ANTHROPIC_API_KEY). See "
            "/docs/ROADMAP.md for the full multi-phase plan (speech, "
            "recommendations, ML, observability)."
        ),
        version="0.3.0",
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

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()

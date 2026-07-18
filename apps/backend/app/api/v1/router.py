"""Aggregates all v1 endpoint routers under a single APIRouter."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    dashboard,
    health,
    memory,
    planner,
    quizzes,
    speech,
    topics,
    tutor,
    users,
    vocabulary,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(dashboard.router)
api_router.include_router(vocabulary.router)
api_router.include_router(topics.router)
api_router.include_router(planner.router)
api_router.include_router(tutor.router)
api_router.include_router(memory.router)
api_router.include_router(quizzes.router)
api_router.include_router(speech.router)

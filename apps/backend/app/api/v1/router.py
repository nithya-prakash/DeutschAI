"""Aggregates all v1 endpoint routers under a single APIRouter."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    dashboard,
    health,
    listening,
    memory,
    planner,
    quizzes,
    reading,
    recommendations,
    speech,
    topics,
    tutor,
    users,
    vocabulary,
    writing,
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
api_router.include_router(reading.router)
api_router.include_router(listening.router)
api_router.include_router(writing.router)
api_router.include_router(speech.router)
api_router.include_router(recommendations.router)
api_router.include_router(admin.router)

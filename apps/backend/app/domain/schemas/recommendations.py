"""Recommendation Engine response schema — internal content only (grammar
topics + vocabulary), ranked by real data (forgetting-curve retention,
mistake history). Podcasts/articles aren't included yet: there's no
external content source integrated (see docs/FEATURES.md's Future Work).
"""
import uuid

from pydantic import BaseModel


class RecommendedVocab(BaseModel):
    id: uuid.UUID
    german: str
    english: str
    retention_probability: float
    reason: str


class RecommendedTopic(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    reason: str


class RecommendationResult(BaseModel):
    vocab: list[RecommendedVocab]
    topics: list[RecommendedTopic]

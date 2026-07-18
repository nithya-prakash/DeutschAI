"""Import every ORM model here so Alembic autogenerate and SQLAlchemy's
mapper configuration see the full metadata graph, and so string-based
`relationship()` type references resolve correctly regardless of import
order elsewhere in the app.
"""
from app.infrastructure.database.base import Base
from app.models.ai_memory import AIMemory
from app.models.conversation import Conversation, ConversationMessage
from app.models.grammar_topic import GrammarTopic
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion
from app.models.study_session import StudySession
from app.models.user import User
from app.models.user_topic_progress import UserTopicProgress
from app.models.vocabulary_item import VocabularyItem

__all__ = [
    "Base",
    "User",
    "StudySession",
    "GrammarTopic",
    "UserTopicProgress",
    "VocabularyItem",
    "AIMemory",
    "QuizQuestion",
    "QuizAttempt",
    "Conversation",
    "ConversationMessage",
]

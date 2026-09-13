"""Import every ORM model here so Alembic autogenerate and SQLAlchemy's
mapper configuration see the full metadata graph, and so string-based
`relationship()` type references resolve correctly regardless of import
order elsewhere in the app.
"""
from app.infrastructure.database.base import Base
from app.models.ai_memory import AIMemory
from app.models.conversation import Conversation, ConversationMessage
from app.models.error_log_entry import ErrorLogEntry
from app.models.grammar_topic import GrammarTopic
from app.models.listening_attempt import ListeningAttempt
from app.models.listening_script import ListeningScript
from app.models.llm_usage_event import LLMUsageEvent
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion
from app.models.reading_attempt import ReadingAttempt
from app.models.reading_passage import ReadingPassage
from app.models.speech_conversation import SpeechConversation, SpeechTurn
from app.models.study_session import StudySession
from app.models.user import User
from app.models.user_topic_progress import UserTopicProgress
from app.models.vocabulary_item import VocabularyItem
from app.models.writing_prompt import WritingPrompt
from app.models.writing_submission import WritingSubmission

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
    "ReadingPassage",
    "ReadingAttempt",
    "ListeningScript",
    "ListeningAttempt",
    "WritingPrompt",
    "WritingSubmission",
    "Conversation",
    "ConversationMessage",
    "SpeechConversation",
    "SpeechTurn",
    "LLMUsageEvent",
    "ErrorLogEntry",
]

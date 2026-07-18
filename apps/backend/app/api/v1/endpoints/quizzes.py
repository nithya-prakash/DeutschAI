"""Assessment Agent / quiz endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.domain.schemas.quiz import QuizAttemptCreate, QuizAttemptResult, QuizQuestionRead
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.assessment_service import (
    AssessmentService,
    NoQuestionsForTopicError,
    QuestionNotFoundError,
)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/topics/{topic_id}/question", response_model=QuizQuestionRead)
async def get_question_for_topic(
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizQuestionRead:
    try:
        return await AssessmentService(db).get_question_for_topic(topic_id)
    except NoQuestionsForTopicError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No quiz questions for this topic"
        ) from err


@router.post("/attempts", response_model=QuizAttemptResult)
async def submit_attempt(
    payload: QuizAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizAttemptResult:
    try:
        return await AssessmentService(db).submit_attempt(
            current_user.id, payload.question_id, payload.selected_option_index
        )
    except QuestionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        ) from err

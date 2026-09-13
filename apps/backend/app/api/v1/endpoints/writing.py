"""Writing exercise endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tutor_agent import LLMNotConfiguredError
from app.api.deps import get_current_user
from app.domain.schemas.writing import (
    WritingPromptRead,
    WritingSubmissionCreate,
    WritingSubmissionResult,
)
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.services.writing_service import (
    NoPromptsAvailableError,
    PromptNotFoundError,
    WritingService,
)

router = APIRouter(prefix="/writing", tags=["writing"])


@router.get("/prompts/random", response_model=WritingPromptRead)
async def get_random_prompt(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WritingPromptRead:
    try:
        return await WritingService(db).get_random_prompt(current_user.cefr_level)
    except NoPromptsAvailableError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No writing prompts available"
        ) from err


@router.post("/submissions", response_model=WritingSubmissionResult)
async def submit_writing(
    payload: WritingSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WritingSubmissionResult:
    try:
        return await WritingService(db).submit_writing(
            current_user, payload.prompt_id, payload.submitted_text
        )
    except PromptNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        ) from err
    except LLMNotConfiguredError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        ) from err

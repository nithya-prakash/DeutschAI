"""Vocabulary notebook business logic — the API-facing wrapper around the
pure SM-2 scheduler in `spaced_repetition.py`."""
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.vocabulary import VocabularyItemCreate, VocabularyItemRead
from app.models.vocabulary_item import DEFAULT_EASE_FACTOR, VocabularyItem
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.spaced_repetition import ReviewQuality, SchedulingState, schedule_next_review


class VocabularyItemNotFoundError(Exception):
    pass


def _to_read_schema(item: VocabularyItem, today: date) -> VocabularyItemRead:
    schema = VocabularyItemRead.model_validate(item)
    schema.is_due = item.next_review_date <= today
    return schema


@dataclass
class VocabularyService:
    session: AsyncSession

    async def list_for_user(self, user_id: uuid.UUID) -> list[VocabularyItemRead]:
        repo = VocabularyRepository(self.session)
        items = await repo.list_for_user(user_id)
        today = datetime.now(UTC).date()
        return [_to_read_schema(item, today) for item in items]

    async def add_word(
        self, user_id: uuid.UUID, payload: VocabularyItemCreate
    ) -> VocabularyItemRead:
        repo = VocabularyRepository(self.session)
        today = datetime.now(UTC).date()
        item = VocabularyItem(
            user_id=user_id,
            german=payload.german,
            english=payload.english,
            example_sentence=payload.example_sentence,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval_days=0,
            repetitions=0,
            next_review_date=today,
        )
        item = await repo.create(item)
        await self.session.commit()
        await self.session.refresh(item)
        return _to_read_schema(item, today)

    async def review_word(
        self, user_id: uuid.UUID, item_id: uuid.UUID, quality: ReviewQuality
    ) -> VocabularyItemRead:
        repo = VocabularyRepository(self.session)
        item = await repo.get_for_user(item_id, user_id)
        if item is None:
            raise VocabularyItemNotFoundError(str(item_id))

        today = datetime.now(UTC).date()
        current_state = SchedulingState(
            ease_factor=item.ease_factor,
            interval_days=item.interval_days,
            repetitions=item.repetitions,
        )
        new_state, next_due = schedule_next_review(current_state, quality, today)

        item.ease_factor = new_state.ease_factor
        item.interval_days = new_state.interval_days
        item.repetitions = new_state.repetitions
        item.next_review_date = next_due
        item.last_reviewed_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(item)
        return _to_read_schema(item, today)

    async def delete_word(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        repo = VocabularyRepository(self.session)
        item = await repo.get_for_user(item_id, user_id)
        if item is None:
            raise VocabularyItemNotFoundError(str(item_id))
        await repo.delete(item)
        await self.session.commit()

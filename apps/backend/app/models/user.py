"""User ORM model.

The `native_language` / `target_language` pair is what lets the platform
support additional languages later without a schema change — a user's
learning progress is always scoped to a `target_language`, never hardcoded
to German.
"""
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.study_session import StudySession


class CEFRLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    native_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    target_language: Mapped[str] = mapped_column(String(10), default="de", nullable=False)
    cefr_level: Mapped[CEFRLevel] = mapped_column(
        Enum(CEFRLevel, name="cefr_level"), default=CEFRLevel.A1, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

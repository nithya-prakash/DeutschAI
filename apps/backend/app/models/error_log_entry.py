"""Local record of unhandled request errors — backs the admin panel's
"Error logs" tab. Written by the global exception handler in
`app/main.py`. Complementary to Sentry (which captures the same exceptions
independently via its own ASGI integration for alerting); this is a
simpler, local, always-available view with no external dependency."""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ErrorLogEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "error_log_entries"

    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    exception_type: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    traceback: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ErrorLogEntry {self.method} {self.path} {self.exception_type}>"

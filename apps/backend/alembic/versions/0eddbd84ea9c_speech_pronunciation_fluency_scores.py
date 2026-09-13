"""Speech pronunciation and fluency scores

Revision ID: 0eddbd84ea9c
Revises: a3c640201063
Create Date: 2026-09-13 00:00:02.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0eddbd84ea9c'
down_revision: str | None = 'a3c640201063'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('speech_turns', sa.Column('pronunciation_score', sa.Integer(), nullable=True))
    op.add_column('speech_turns', sa.Column('fluency_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('speech_turns', 'fluency_score')
    op.drop_column('speech_turns', 'pronunciation_score')

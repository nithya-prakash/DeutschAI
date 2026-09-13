"""Writing prompts and submissions

Revision ID: a3c640201063
Revises: 83c3223d4ae6
Create Date: 2026-09-13 00:00:01.000000
"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.domain.writing_reference import WRITING_PROMPTS

# revision identifiers, used by Alembic.
revision: str = 'a3c640201063'
down_revision: str | None = '83c3223d4ae6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# cefr_level already exists (created by 49a41b29b2d9 for users.cefr_level) —
# postgresql.ENUM(create_type=False) so this doesn't try to CREATE TYPE it again.
_cefr_level_enum = postgresql.ENUM(
    'A1', 'A2', 'B1', 'B2', 'C1', 'C2', name='cefr_level', create_type=False
)

writing_prompt_table = sa.table(
    "writing_prompts",
    sa.column("id", sa.Uuid()),
    sa.column("cefr_level", _cefr_level_enum),
    sa.column("prompt_text", sa.Text()),
)


def upgrade() -> None:
    op.create_table(
        'writing_prompts',
        sa.Column('cefr_level', _cefr_level_enum, nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_writing_prompts_cefr_level'), 'writing_prompts', ['cefr_level'], unique=False
    )

    op.create_table(
        'writing_submissions',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('prompt_id', sa.Uuid(), nullable=False),
        sa.Column('submitted_text', sa.Text(), nullable=False),
        sa.Column('grammar_score', sa.Integer(), nullable=True),
        sa.Column('vocabulary_score', sa.Integer(), nullable=True),
        sa.Column('task_completion_score', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prompt_id'], ['writing_prompts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_writing_submissions_prompt_id'), 'writing_submissions', ['prompt_id'], unique=False
    )
    op.create_index(
        op.f('ix_writing_submissions_user_id'), 'writing_submissions', ['user_id'], unique=False
    )

    op.bulk_insert(
        writing_prompt_table,
        [
            {"id": uuid.uuid4(), "cefr_level": cefr_level, "prompt_text": prompt_text}
            for cefr_level, prompt_text in WRITING_PROMPTS
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_writing_submissions_user_id'), table_name='writing_submissions')
    op.drop_index(op.f('ix_writing_submissions_prompt_id'), table_name='writing_submissions')
    op.drop_table('writing_submissions')
    op.drop_index(op.f('ix_writing_prompts_cefr_level'), table_name='writing_prompts')
    op.drop_table('writing_prompts')

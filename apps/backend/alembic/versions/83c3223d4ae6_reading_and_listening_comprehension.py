"""Reading and listening comprehension

Revision ID: 83c3223d4ae6
Revises: f1a2b3c4d5e6
Create Date: 2026-09-13 00:00:00.000000
"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.domain.listening_reference import LISTENING_SCRIPTS
from app.domain.reading_reference import READING_PASSAGES

# revision identifiers, used by Alembic.
revision: str = '83c3223d4ae6'
down_revision: str | None = 'f1a2b3c4d5e6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# cefr_level already exists (created by 49a41b29b2d9 for users.cefr_level) —
# postgresql.ENUM(create_type=False) so this doesn't try to CREATE TYPE it again.
_cefr_level_enum = postgresql.ENUM(
    'A1', 'A2', 'B1', 'B2', 'C1', 'C2', name='cefr_level', create_type=False
)

reading_passage_table = sa.table(
    "reading_passages",
    sa.column("id", sa.Uuid()),
    sa.column("cefr_level", _cefr_level_enum),
    sa.column("passage_text", sa.Text()),
    sa.column("question", sa.Text()),
    sa.column("options", sa.JSON().with_variant(postgresql.JSONB(), "postgresql")),
    sa.column("correct_option_index", sa.Integer()),
    sa.column("explanation", sa.Text()),
)

listening_script_table = sa.table(
    "listening_scripts",
    sa.column("id", sa.Uuid()),
    sa.column("cefr_level", _cefr_level_enum),
    sa.column("script_text", sa.Text()),
    sa.column("audio_object_key", sa.Text()),
    sa.column("question", sa.Text()),
    sa.column("options", sa.JSON().with_variant(postgresql.JSONB(), "postgresql")),
    sa.column("correct_option_index", sa.Integer()),
    sa.column("explanation", sa.Text()),
)


def upgrade() -> None:
    op.create_table(
        'reading_passages',
        sa.Column('cefr_level', _cefr_level_enum, nullable=False),
        sa.Column('passage_text', sa.Text(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column(
            'options', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'),
            nullable=False,
        ),
        sa.Column('correct_option_index', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_reading_passages_cefr_level'), 'reading_passages', ['cefr_level'], unique=False
    )

    op.create_table(
        'reading_attempts',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('passage_id', sa.Uuid(), nullable=False),
        sa.Column('selected_option_index', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['passage_id'], ['reading_passages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_reading_attempts_passage_id'), 'reading_attempts', ['passage_id'], unique=False
    )
    op.create_index(
        op.f('ix_reading_attempts_user_id'), 'reading_attempts', ['user_id'], unique=False
    )

    op.create_table(
        'listening_scripts',
        sa.Column('cefr_level', _cefr_level_enum, nullable=False),
        sa.Column('script_text', sa.Text(), nullable=False),
        sa.Column('audio_object_key', sa.Text(), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column(
            'options', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'),
            nullable=False,
        ),
        sa.Column('correct_option_index', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_listening_scripts_cefr_level'), 'listening_scripts', ['cefr_level'], unique=False
    )

    op.create_table(
        'listening_attempts',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('script_id', sa.Uuid(), nullable=False),
        sa.Column('selected_option_index', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['script_id'], ['listening_scripts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_listening_attempts_script_id'), 'listening_attempts', ['script_id'], unique=False
    )
    op.create_index(
        op.f('ix_listening_attempts_user_id'), 'listening_attempts', ['user_id'], unique=False
    )

    op.bulk_insert(
        reading_passage_table,
        [
            {
                "id": uuid.uuid4(),
                "cefr_level": cefr_level,
                "passage_text": passage_text,
                "question": question,
                "options": options,
                "correct_option_index": correct_index,
                "explanation": explanation,
            }
            for cefr_level, passage_text, question, options, correct_index, explanation in READING_PASSAGES
        ],
    )

    op.bulk_insert(
        listening_script_table,
        [
            {
                "id": uuid.uuid4(),
                "cefr_level": cefr_level,
                "script_text": script_text,
                "audio_object_key": None,
                "question": question,
                "options": options,
                "correct_option_index": correct_index,
                "explanation": explanation,
            }
            for cefr_level, script_text, question, options, correct_index, explanation in LISTENING_SCRIPTS
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_listening_attempts_user_id'), table_name='listening_attempts')
    op.drop_index(op.f('ix_listening_attempts_script_id'), table_name='listening_attempts')
    op.drop_table('listening_attempts')
    op.drop_index(op.f('ix_listening_scripts_cefr_level'), table_name='listening_scripts')
    op.drop_table('listening_scripts')
    op.drop_index(op.f('ix_reading_attempts_user_id'), table_name='reading_attempts')
    op.drop_index(op.f('ix_reading_attempts_passage_id'), table_name='reading_attempts')
    op.drop_table('reading_attempts')
    op.drop_index(op.f('ix_reading_passages_cefr_level'), table_name='reading_passages')
    op.drop_table('reading_passages')

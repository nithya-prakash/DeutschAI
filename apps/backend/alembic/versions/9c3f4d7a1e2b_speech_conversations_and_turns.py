"""Phase 4: speech conversations and turns

Revision ID: 9c3f4d7a1e2b
Revises: 4bdbac7f97ac
Create Date: 2026-07-18 10:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9c3f4d7a1e2b'
down_revision: str | None = '4bdbac7f97ac'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'speech_conversations',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_speech_conversations_user_id'), 'speech_conversations', ['user_id'], unique=False
    )
    op.create_table(
        'speech_turns',
        sa.Column('speech_conversation_id', sa.Uuid(), nullable=False),
        # message_role already exists (created by 4bdbac7f97ac for conversation_messages) —
        # postgresql.ENUM(create_type=False) so this doesn't try to CREATE TYPE it again.
        sa.Column(
            'role',
            postgresql.ENUM('USER', 'ASSISTANT', name='message_role', create_type=False),
            nullable=False,
        ),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('audio_object_key', sa.Text(), nullable=False),
        sa.Column('grammar_score', sa.Integer(), nullable=True),
        sa.Column('vocabulary_score', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['speech_conversation_id'], ['speech_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_speech_turns_speech_conversation_id'), 'speech_turns', ['speech_conversation_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_speech_turns_speech_conversation_id'), table_name='speech_turns')
    op.drop_table('speech_turns')
    op.drop_index(op.f('ix_speech_conversations_user_id'), table_name='speech_conversations')
    op.drop_table('speech_conversations')

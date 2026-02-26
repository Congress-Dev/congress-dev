"""Add user_interest and user_interest_usc_content tables

Revision ID: a1b2c3d4e5f6
Revises: c9d7e37be069
Create Date: 2026-02-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c9d7e37be069'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_interest',
        sa.Column('user_interest_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('interest_text', sa.String(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['sensitive.user_ident.user_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('user_interest_id'),
        schema='sensitive',
    )
    op.create_index(
        'ix_sensitive_user_interest_user_id',
        'user_interest',
        ['user_id'],
        schema='sensitive',
    )

    op.create_table(
        'user_interest_usc_content',
        sa.Column('user_interest_usc_content_id', sa.Integer(), nullable=False),
        sa.Column('user_interest_id', sa.Integer(), nullable=True),
        sa.Column('usc_ident', sa.String(), nullable=True),
        sa.Column('match_source', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('match_rank', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ['user_interest_id'],
            ['sensitive.user_interest.user_interest_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('user_interest_usc_content_id'),
        schema='sensitive',
    )
    op.create_index(
        'ix_sensitive_user_interest_usc_content_user_interest_id',
        'user_interest_usc_content',
        ['user_interest_id'],
        schema='sensitive',
    )
    op.create_index(
        'ix_sensitive_user_interest_usc_content_usc_ident',
        'user_interest_usc_content',
        ['usc_ident'],
        schema='sensitive',
    )


def downgrade() -> None:
    op.drop_index(
        'ix_sensitive_user_interest_usc_content_usc_ident',
        table_name='user_interest_usc_content',
        schema='sensitive',
    )
    op.drop_index(
        'ix_sensitive_user_interest_usc_content_user_interest_id',
        table_name='user_interest_usc_content',
        schema='sensitive',
    )
    op.drop_table('user_interest_usc_content', schema='sensitive')
    op.drop_index(
        'ix_sensitive_user_interest_user_id',
        table_name='user_interest',
        schema='sensitive',
    )
    op.drop_table('user_interest', schema='sensitive')

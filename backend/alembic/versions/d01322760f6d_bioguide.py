"""bioguide

Revision ID: d01322760f6d
Revises: af9ab9994117
Create Date: 2025-01-11 03:05:34.385263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd01322760f6d'
down_revision: Union[str, None] = 'af9ab9994117'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_index(op.f('ix_sensitive_user_legislator_user_id'), table_name='user_legislator', schema='sensitive')
    op.drop_index(op.f('ix_sensitive_user_legislator_legislator_id'), table_name='user_legislator', schema='sensitive')
    op.drop_table('user_legislator', schema='sensitive')

    op.create_table('user_legislator',
    sa.Column('user_legislator_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('bioguide_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['bioguide_id'], ['legislator.bioguide_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['sensitive.user_ident.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_legislator_id'),
    schema='sensitive'
    )
    op.create_index(op.f('ix_sensitive_user_legislator_bioguide_id'), 'user_legislator', ['bioguide_id'], unique=False, schema='sensitive')
    op.create_index(op.f('ix_sensitive_user_legislator_user_id'), 'user_legislator', ['user_id'], unique=False, schema='sensitive')

def downgrade():
    op.drop_index(op.f('ix_sensitive_user_legislator_user_id'), table_name='user_legislator', schema='sensitive')
    op.drop_index(op.f('ix_sensitive_user_legislator_bioguide_id'), table_name='user_legislator', schema='sensitive')
    op.drop_table('user_legislator', schema='sensitive')

    op.create_table('user_legislator',
    sa.Column('user_legislator_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('legislator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['legislator_id'], ['legislator.legislator_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['sensitive.user_ident.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_legislator_id'),
    schema='sensitive'
    )
    op.create_index(op.f('ix_sensitive_user_legislator_legislator_id'), 'user_legislator', ['legislator_id'], unique=False, schema='sensitive')
    op.create_index(op.f('ix_sensitive_user_legislator_user_id'), 'user_legislator', ['user_id'], unique=False, schema='sensitive')
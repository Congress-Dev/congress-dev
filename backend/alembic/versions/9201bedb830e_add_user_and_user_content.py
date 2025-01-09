"""Add user and user content

Revision ID: 9201bedb830e
Revises: bf2269ea67a1
Create Date: 2025-01-08 23:16:21.332392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9201bedb830e'
down_revision: Union[str, None] = 'bf2269ea67a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_ident',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('user_first_name', sa.String(), nullable=False),
    sa.Column('user_last_name', sa.String(), nullable=False),
    sa.Column('user_state', sa.String(), nullable=True),
    sa.Column('user_image', sa.String(), nullable=True),
    sa.Column('user_auth_password', sa.String(), nullable=True),
    sa.Column('user_auth_google', sa.String(), nullable=True),
    sa.Column('user_auth_expiration', sa.DateTime(), nullable=True),
    sa.Column('user_auth_cookie', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('user_legislator',
    sa.Column('user_legislator_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('legislator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['legislator_id'], ['legislator.legislator_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user_ident.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_legislator_id')
    )
    op.create_index(op.f('ix_user_legislator_legislator_id'), 'user_legislator', ['legislator_id'], unique=False)
    op.create_index(op.f('ix_user_legislator_user_id'), 'user_legislator', ['user_id'], unique=False)
    op.create_table('user_legislation',
    sa.Column('user_legislation_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('legislation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['legislation_id'], ['legislation.legislation_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user_ident.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_legislation_id')
    )
    op.create_index(op.f('ix_user_legislation_legislation_id'), 'user_legislation', ['legislation_id'], unique=False)
    op.create_index(op.f('ix_user_legislation_user_id'), 'user_legislation', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_legislation')
    op.drop_table('user_legislator')
    op.drop_table('user_ident')
    # ### end Alembic commands ###

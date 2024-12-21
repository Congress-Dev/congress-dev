"""Add prompts schema

Revision ID: 9a72e5faa767
Revises: 1d773a33ec53
Create Date: 2024-12-18 21:02:06.298753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema

# revision identifiers, used by Alembic.
revision: str = '9a72e5faa767'
down_revision: Union[str, None] = '1d773a33ec53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(CreateSchema("prompts", if_not_exists=True))
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prompt',
    sa.Column('prompt_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('prompt', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('prompt_id'),
    schema='prompts'
    )
    op.create_table('prompt_batch',
    sa.Column('prompt_batch_id', sa.Integer(), nullable=False),
    sa.Column('prompt_id', sa.Integer(), nullable=True),
    sa.Column('legislation_version_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('attempted', sa.Integer(), nullable=False),
    sa.Column('successful', sa.Integer(), nullable=False),
    sa.Column('failed', sa.Integer(), nullable=False),
    sa.Column('skipped', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['legislation_version_id'], ['legislation_version.legislation_version_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prompt_id'], ['prompts.prompt.prompt_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('prompt_batch_id'),
    schema='prompts'
    )
    op.create_index(op.f('ix_prompts_prompt_batch_legislation_version_id'), 'prompt_batch', ['legislation_version_id'], unique=False, schema='prompts')
    op.create_index(op.f('ix_prompts_prompt_batch_prompt_id'), 'prompt_batch', ['prompt_id'], unique=False, schema='prompts')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_prompts_prompt_batch_prompt_id'), table_name='prompt_batch', schema='prompts')
    op.drop_index(op.f('ix_prompts_prompt_batch_legislation_version_id'), table_name='prompt_batch', schema='prompts')
    op.drop_table('prompt_batch', schema='prompts')
    op.drop_table('prompt', schema='prompts')
    # ### end Alembic commands ###
"""Fix spelling mistake

Revision ID: 56f054b7ccfb
Revises: 52bde36f1f81
Create Date: 2024-01-10 21:40:49.697708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56f054b7ccfb'
down_revision: Union[str, None] = '52bde36f1f81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_legislation_committee_association_legsilation_id', table_name='legislation_committee_association')
    op.drop_constraint('legislation_committee_association_legsilation_id_fkey', 'legislation_committee_association', type_='foreignkey')
    op.drop_column('legislation_committee_association', 'legsilation_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('legislation_committee_association', sa.Column('legsilation_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('legislation_committee_association_legsilation_id_fkey', 'legislation_committee_association', 'legislation', ['legsilation_id'], ['legislation_id'])
    op.create_index('ix_legislation_committee_association_legsilation_id', 'legislation_committee_association', ['legsilation_id'], unique=False)
    # ### end Alembic commands ###

"""Policy Area and Subject

Revision ID: 1d19f9457c13
Revises: 56f054b7ccfb
Create Date: 2024-01-10 22:31:09.332887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d19f9457c13'
down_revision: Union[str, None] = '56f054b7ccfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'legislative_policy_area_association', 'legislative_policy_area', ['legislative_policy_area_id'], ['legislative_policy_area_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'legislative_policy_area_association', type_='foreignkey')
    # ### end Alembic commands ###

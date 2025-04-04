"""create summary table

Revision ID: a3b78ac73761
Revises: 82a79ee10856
Create Date: 2024-12-24 20:47:35.698173

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a3b78ac73761"
down_revision: Union[str, None] = "82a79ee10856"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "legislation_content_summary",
        sa.Column("legislation_content_summary_id", sa.Integer(), nullable=False),
        sa.Column("legislation_content_id", sa.Integer(), nullable=True),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("prompt_batch_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["legislation_content_id"],
            ["legislation_content.legislation_content_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prompt_batch_id"],
            ["prompts.prompt_batch.prompt_batch_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("legislation_content_summary_id"),
    )
    op.create_index(
        op.f("ix_legislation_content_summary_legislation_content_id"),
        "legislation_content_summary",
        ["legislation_content_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislation_content_summary_prompt_batch_id"),
        "legislation_content_summary",
        ["prompt_batch_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_legislation_content_summary_prompt_batch_id"),
        table_name="legislation_content_summary",
    )
    op.drop_index(
        op.f("ix_legislation_content_summary_legislation_content_id"),
        table_name="legislation_content_summary",
    )
    op.drop_table("legislation_content_summary")
    # ### end Alembic commands ###

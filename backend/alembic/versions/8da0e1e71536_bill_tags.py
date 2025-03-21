"""bill tags

Revision ID: 8da0e1e71536
Revises: 45716515aad4
Create Date: 2025-02-16 02:39:37.137697

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8da0e1e71536"
down_revision: Union[str, None] = "45716515aad4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "legislation_version_tag",
        sa.Column("legislation_version_tag_id", sa.Integer(), nullable=False),
        sa.Column("legislation_version_id", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("prompt_batch_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["legislation_version_id"],
            ["legislation_version.legislation_version_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prompt_batch_id"],
            ["prompts.prompt_batch.prompt_batch_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("legislation_version_tag_id"),
    )
    op.create_index(
        op.f("ix_legislation_version_tag_legislation_version_id"),
        "legislation_version_tag",
        ["legislation_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislation_version_tag_prompt_batch_id"),
        "legislation_version_tag",
        ["prompt_batch_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislation_version_tag_tags"),
        "legislation_version_tag",
        ["tags"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_legislation_version_tag_tags"), table_name="legislation_version_tag"
    )
    op.drop_index(
        op.f("ix_legislation_version_tag_prompt_batch_id"),
        table_name="legislation_version_tag",
    )
    op.drop_index(
        op.f("ix_legislation_version_tag_legislation_version_id"),
        table_name="legislation_version_tag",
    )
    op.drop_table("legislation_version_tag")
    # ### end Alembic commands ###

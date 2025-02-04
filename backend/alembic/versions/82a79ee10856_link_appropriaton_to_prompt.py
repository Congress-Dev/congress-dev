"""link appropriaton to prompt

Revision ID: 82a79ee10856
Revises: f6488f13146c
Create Date: 2024-12-24 15:36:27.865435

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "82a79ee10856"
down_revision: Union[str, None] = "f6488f13146c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appropriation",
        sa.Column("prompt_batch_id", sa.INTEGER(), autoincrement=False, nullable=False),
        schema="appropriations",
    )
    op.create_foreign_key(
        "appropriation_prompt_batch_id_fk",
        "appropriation",
        "prompt_batch",
        ["prompt_batch_id"],
        ["prompt_batch_id"],
        source_schema="appropriations",  # Source schema
        referent_schema="prompts",  # Target schema
        ondelete="CASCADE",  # Optional: specify ON DELETE behavior)
    )
    op.drop_constraint(
        "legislation_content_tag_prompt_batch_id_fkey",
        "legislation_content_tag",
        type_="foreignkey",
        schema="public",
    )

    # Create a new foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        "legislation_content_tag_prompt_batch_id_fkey",
        "legislation_content_tag",
        "prompt_batch",
        ["prompt_batch_id"],
        ["prompt_batch_id"],
        source_schema="public",
        referent_schema="prompts",
        ondelete="CASCADE",
    )
    # ### commands auto generated by Alembic - please adjust! ###

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    pass

"""appripriations

Revision ID: 1d773a33ec53
Revises: 56f054b7ccfb
Create Date: 2024-02-03 22:35:01.877361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema

# revision identifiers, used by Alembic.
revision: str = "1d773a33ec53"
down_revision: Union[str, None] = "56f054b7ccfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(CreateSchema("appropriations", if_not_exists=True))
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "legislative_policy_area",
        sa.Column("legislative_policy_area_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("congress_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["congress_id"], ["congress.congress_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("legislative_policy_area_id"),
        sa.UniqueConstraint("name", "congress_id", name="unq_leg_pol"),
    )
    op.create_index(
        op.f("ix_legislative_policy_area_congress_id"),
        "legislative_policy_area",
        ["congress_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislative_policy_area_name"),
        "legislative_policy_area",
        ["name"],
        unique=True,
    )
    op.create_table(
        "legislative_subject",
        sa.Column("legislative_subject_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("congress_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["congress_id"], ["congress.congress_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("legislative_subject_id"),
        sa.UniqueConstraint("subject", "congress_id", name="unq_leg_subj"),
    )
    op.create_index(
        op.f("ix_legislative_subject_congress_id"),
        "legislative_subject",
        ["congress_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislative_subject_subject"),
        "legislative_subject",
        ["subject"],
        unique=False,
    )
    op.create_table(
        "legislative_policy_area_association",
        sa.Column(
            "legislative_policy_area_association_id", sa.Integer(), nullable=False
        ),
        sa.Column("legislative_policy_area_id", sa.Integer(), nullable=True),
        sa.Column("legislation_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["legislation_id"], ["legislation.legislation_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["legislative_policy_area_id"],
            ["legislative_policy_area.legislative_policy_area_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("legislative_policy_area_association_id"),
    )
    op.create_index(
        op.f("ix_legislative_policy_area_association_legislation_id"),
        "legislative_policy_area_association",
        ["legislation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislative_policy_area_association_legislative_policy_area_id"),
        "legislative_policy_area_association",
        ["legislative_policy_area_id"],
        unique=False,
    )
    op.create_table(
        "legislative_subject_association",
        sa.Column("legislative_subject_association_id", sa.Integer(), nullable=False),
        sa.Column("legislative_subject_id", sa.Integer(), nullable=True),
        sa.Column("legislation_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["legislation_id"], ["legislation.legislation_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["legislative_subject_id"],
            ["legislative_subject.legislative_subject_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("legislative_subject_association_id"),
    )
    op.create_index(
        op.f("ix_legislative_subject_association_legislation_id"),
        "legislative_subject_association",
        ["legislation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_legislative_subject_association_legislative_subject_id"),
        "legislative_subject_association",
        ["legislative_subject_id"],
        unique=False,
    )
    op.create_table(
        "appropriation",
        sa.Column("appropriation_id", sa.Integer(), nullable=False),
        sa.Column("legislation_version_id", sa.Integer(), nullable=True),
        sa.Column("legislation_content_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("new_spending", sa.Boolean(), nullable=False),
        sa.Column("fiscal_years", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("until_expended", sa.Boolean(), nullable=False),
        sa.Column("expiration_year", sa.Integer(), nullable=True),
        sa.Column("target", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["legislation_content_id"],
            ["legislation_content.legislation_content_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["legislation_version_id"],
            ["legislation_version.legislation_version_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("appropriation_id"),
        schema="appropriations",
    )
    op.create_index(
        op.f("ix_appropriations_appropriation_fiscal_years"),
        "appropriation",
        ["fiscal_years"],
        unique=False,
        schema="appropriations",
    )
    op.create_index(
        op.f("ix_appropriations_appropriation_legislation_content_id"),
        "appropriation",
        ["legislation_content_id"],
        unique=False,
        schema="appropriations",
    )
    op.create_index(
        op.f("ix_appropriations_appropriation_legislation_version_id"),
        "appropriation",
        ["legislation_version_id"],
        unique=False,
        schema="appropriations",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_appropriations_appropriation_legislation_version_id"),
        table_name="appropriation",
        schema="appropriations",
    )
    op.drop_index(
        op.f("ix_appropriations_appropriation_legislation_content_id"),
        table_name="appropriation",
        schema="appropriations",
    )
    op.drop_index(
        op.f("ix_appropriations_appropriation_fiscal_years"),
        table_name="appropriation",
        schema="appropriations",
    )
    op.drop_table("appropriation", schema="appropriations")
    op.drop_index(
        op.f("ix_legislative_subject_association_legislative_subject_id"),
        table_name="legislative_subject_association",
    )
    op.drop_index(
        op.f("ix_legislative_subject_association_legislation_id"),
        table_name="legislative_subject_association",
    )
    op.drop_table("legislative_subject_association")
    op.drop_index(
        op.f("ix_legislative_policy_area_association_legislative_policy_area_id"),
        table_name="legislative_policy_area_association",
    )
    op.drop_index(
        op.f("ix_legislative_policy_area_association_legislation_id"),
        table_name="legislative_policy_area_association",
    )
    op.drop_table("legislative_policy_area_association")
    op.drop_index(
        op.f("ix_legislative_subject_subject"), table_name="legislative_subject"
    )
    op.drop_index(
        op.f("ix_legislative_subject_congress_id"), table_name="legislative_subject"
    )
    op.drop_table("legislative_subject")
    op.drop_index(
        op.f("ix_legislative_policy_area_name"), table_name="legislative_policy_area"
    )
    op.drop_index(
        op.f("ix_legislative_policy_area_congress_id"),
        table_name="legislative_policy_area",
    )
    op.drop_table("legislative_policy_area")
    # ### end Alembic commands ###
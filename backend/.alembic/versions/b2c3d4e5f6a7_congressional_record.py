"""Add Congressional Record tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create CRECSection enum type
    crec_section = sa.Enum('Senate', 'House', 'Extensions', 'DailyDigest', name='crecsection')
    crec_section.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'crec_issue',
        sa.Column('crec_issue_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('congress_id', sa.Integer(), sa.ForeignKey('congress.congress_id', ondelete='CASCADE'), nullable=True),
        sa.Column('package_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_crec_issue_issue_date', 'crec_issue', ['issue_date'], unique=True)
    op.create_index('ix_crec_issue_congress_id', 'crec_issue', ['congress_id'])
    op.create_unique_constraint('uq_crec_issue_package_id', 'crec_issue', ['package_id'])

    op.create_table(
        'crec_granule',
        sa.Column('crec_granule_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('crec_issue_id', sa.Integer(), sa.ForeignKey('crec_issue.crec_issue_id', ondelete='CASCADE'), nullable=True),
        sa.Column('granule_id', sa.String(), nullable=True),
        sa.Column('section', crec_section, nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('page_start', sa.String(), nullable=True),
        sa.Column('page_end', sa.String(), nullable=True),
        sa.Column('order_number', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_crec_granule_crec_issue_id', 'crec_granule', ['crec_issue_id'])
    op.create_index('ix_crec_granule_section', 'crec_granule', ['section'])
    op.create_unique_constraint('uq_crec_granule_granule_id', 'crec_granule', ['granule_id'])

    op.create_table(
        'crec_speech',
        sa.Column('crec_speech_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('crec_granule_id', sa.Integer(), sa.ForeignKey('crec_granule.crec_granule_id', ondelete='CASCADE'), nullable=True),
        sa.Column('speaker_raw', sa.String(), nullable=True),
        sa.Column('legislator_bioguide_id', sa.String(), sa.ForeignKey('legislator.bioguide_id', ondelete='SET NULL'), nullable=True),
        sa.Column('order_number', sa.Integer(), default=0),
        sa.Column('content_text', sa.String(), nullable=True),
        sa.Column('word_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_crec_speech_crec_granule_id', 'crec_speech', ['crec_granule_id'])
    op.create_index('ix_crec_speech_legislator_bioguide_id', 'crec_speech', ['legislator_bioguide_id'])

    op.create_table(
        'crec_bill_reference',
        sa.Column('crec_bill_reference_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('crec_speech_id', sa.Integer(), sa.ForeignKey('crec_speech.crec_speech_id', ondelete='CASCADE'), nullable=True),
        sa.Column('legislation_id', sa.Integer(), sa.ForeignKey('legislation.legislation_id', ondelete='SET NULL'), nullable=True),
        sa.Column('cite_text', sa.String(), nullable=True),
        sa.Column('cite_type', sa.String(), nullable=True),
        sa.Column('start_offset', sa.Integer(), nullable=True),
        sa.Column('end_offset', sa.Integer(), nullable=True),
    )
    op.create_index('ix_crec_bill_reference_crec_speech_id', 'crec_bill_reference', ['crec_speech_id'])
    op.create_index('ix_crec_bill_reference_legislation_id', 'crec_bill_reference', ['legislation_id'])

    op.create_table(
        'crec_summary',
        sa.Column('crec_summary_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('crec_granule_id', sa.Integer(), sa.ForeignKey('crec_granule.crec_granule_id', ondelete='CASCADE'), nullable=True),
        sa.Column('crec_issue_id', sa.Integer(), sa.ForeignKey('crec_issue.crec_issue_id', ondelete='CASCADE'), nullable=True),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('summary_type', sa.String(), nullable=True),
        sa.Column('prompt_batch_id', sa.Integer(), sa.ForeignKey('prompts.prompt_batch.prompt_batch_id', ondelete='CASCADE'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        schema='prompts',
    )
    op.create_index('ix_crec_summary_crec_granule_id', 'crec_summary', ['crec_granule_id'], schema='prompts')
    op.create_index('ix_crec_summary_crec_issue_id', 'crec_summary', ['crec_issue_id'], schema='prompts')
    op.create_index('ix_crec_summary_prompt_batch_id', 'crec_summary', ['prompt_batch_id'], schema='prompts')


def downgrade() -> None:
    op.drop_table('crec_summary', schema='prompts')
    op.drop_table('crec_bill_reference')
    op.drop_table('crec_speech')
    op.drop_table('crec_granule')
    op.drop_table('crec_issue')
    sa.Enum(name='crecsection').drop(op.get_bind(), checkfirst=True)

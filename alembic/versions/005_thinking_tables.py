"""thinking tables

Revision ID: 005
Revises: 004
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types
    # -------------------------------------------------------------------------
    bidstatus_enum = postgresql.ENUM(
        'PENDING', 'ACCEPTED', 'REJECTED', 'COUNTERED',
        name='bidstatus', create_type=True
    )
    bidstatus_enum.create(op.get_bind(), checkfirst=True)

    problemstatus_enum = postgresql.ENUM(
        'OPEN', 'COMPLETED', 'EXPIRED',
        name='problemstatus', create_type=True
    )
    problemstatus_enum.create(op.get_bind(), checkfirst=True)

    solutionstatus_enum = postgresql.ENUM(
        'CLAIMED', 'DONE', 'VERIFIED',
        name='solutionstatus', create_type=True
    )
    solutionstatus_enum.create(op.get_bind(), checkfirst=True)

    reflectionstatus_enum = postgresql.ENUM(
        'PENDING', 'SUBMITTED', 'REWARDED',
        name='reflectionstatus', create_type=True
    )
    reflectionstatus_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables
    # -------------------------------------------------------------------------

    # task_bids
    op.create_table(
        'task_bids',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('proof_image_url', sa.String(255), nullable=True),
        sa.Column('proposed_coins', sa.BigInteger(), nullable=False),
        sa.Column('final_coins', sa.BigInteger(), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'ACCEPTED', 'REJECTED', 'COUNTERED', name='bidstatus', create_type=False), server_default='PENDING'),
        sa.Column('parent_comment', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )

    # problem_boards
    op.create_table(
        'problem_boards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('reward_coins', sa.BigInteger(), nullable=False),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', postgresql.ENUM('OPEN', 'COMPLETED', 'EXPIRED', name='problemstatus', create_type=False), server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # problem_solutions
    op.create_table(
        'problem_solutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('board_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('problem_boards.id'), nullable=False, index=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('task_description', sa.String(200), nullable=False),
        sa.Column('status', postgresql.ENUM('CLAIMED', 'DONE', 'VERIFIED', name='solutionstatus', create_type=False), server_default='CLAIMED'),
        sa.Column('proof_image_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # weekly_reflections
    op.create_table(
        'weekly_reflections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('q1_answer', sa.Text(), nullable=True),
        sa.Column('q2_answer', sa.Text(), nullable=True),
        sa.Column('q3_answer', sa.Text(), nullable=True),
        sa.Column('bonus_coins', sa.Integer(), server_default='0'),
        sa.Column('status', postgresql.ENUM('PENDING', 'SUBMITTED', 'REWARDED', name='reflectionstatus', create_type=False), server_default='PENDING'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('kid_id', 'week_start', name='uq_kid_week_reflection'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('weekly_reflections')
    op.drop_table('problem_solutions')
    op.drop_table('problem_boards')
    op.drop_table('task_bids')

    # Drop enum types
    postgresql.ENUM(name='reflectionstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='solutionstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='problemstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='bidstatus').drop(op.get_bind(), checkfirst=True)

"""social extension

Revision ID: 006
Revises: 005
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types
    # -------------------------------------------------------------------------
    challengestatus_enum = postgresql.ENUM(
        'ACTIVE', 'COMPLETED', 'EXPIRED',
        name='challengestatus', create_type=True
    )
    challengestatus_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables
    # -------------------------------------------------------------------------

    # wall_of_fame
    op.create_table(
        'wall_of_fame',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False, index=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('image_url', sa.String(255), nullable=True),
        sa.Column('caption', sa.String(500), nullable=False),
        sa.Column('task_log_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('task_logs.id'), nullable=True),
        sa.Column('likes_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # wall_likes
    op.create_table(
        'wall_likes',
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('wall_of_fame.id'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
    )

    # family_challenges
    op.create_table(
        'family_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('target_count', sa.Integer(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('reward_coins', sa.BigInteger(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'COMPLETED', 'EXPIRED', name='challengestatus', create_type=False), server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # challenge_progress
    op.create_table(
        'challenge_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('family_challenges.id'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('proof_image_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('challenge_id', 'user_id', 'check_in_date', name='uq_challenge_user_date'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('challenge_progress')
    op.drop_table('family_challenges')
    op.drop_table('wall_likes')
    op.drop_table('wall_of_fame')

    # Drop enum types
    postgresql.ENUM(name='challengestatus').drop(op.get_bind(), checkfirst=True)

"""gamification tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-01 00:00:00.000000

Creates Gamification tables:
- user_levels
- user_streaks
- avatar_items
- user_avatar_items
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types
    # -------------------------------------------------------------------------
    itemtype_enum = postgresql.ENUM(
        'FRAME', 'BACKGROUND', 'BADGE', 'ACCESSORY',
        name='itemtype', create_type=False
    )
    itemtype_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables
    # -------------------------------------------------------------------------

    # 2.1 user_levels (lookup table, no FK dependencies)
    op.create_table(
        'user_levels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('level', sa.Integer(), unique=True, nullable=False),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('xp_required', sa.BigInteger(), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=True),
    )

    # 2.2 user_streaks (FK → users.id)
    op.create_table(
        'user_streaks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('current_streak', sa.Integer(), server_default='0'),
        sa.Column('longest_streak', sa.Integer(), server_default='0'),
        sa.Column('last_active_date', sa.Date(), nullable=True),
        sa.Column('streak_bonus_active', sa.Boolean(), server_default='false'),
        sa.Column('streak_frozen_until', sa.Date(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('longest_streak >= current_streak', name='chk_streak_longest_gte_current'),
    )

    # 2.3 avatar_items (catalog, no FK dependencies)
    op.create_table(
        'avatar_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('item_type', postgresql.ENUM('FRAME', 'BACKGROUND', 'BADGE', 'ACCESSORY', name='itemtype', create_type=False), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=False),
        sa.Column('price_coin', sa.Integer(), nullable=False),
        sa.Column('min_level', sa.Integer(), server_default='1'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
    )

    # 2.4 user_avatar_items (inventory, FK → users.id, avatar_items.id)
    op.create_table(
        'user_avatar_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('avatar_items.id'), nullable=False),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_equipped', sa.Boolean(), server_default='false'),
        sa.UniqueConstraint('user_id', 'item_id', name='uq_user_avatar_item'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_avatar_items')
    op.drop_table('avatar_items')
    op.drop_table('user_streaks')
    op.drop_table('user_levels')

    # Drop enum type
    postgresql.ENUM(name='itemtype').drop(op.get_bind(), checkfirst=True)

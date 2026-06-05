"""Play policy: consent, screen time, memory split

Revision ID: 019_play_policy
Revises: 018_play_hub_zones
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "019_play_policy"
down_revision = "018_play_hub_zones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "play_kid_consents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("kid_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("consent_type", sa.String(32), nullable=False),
        sa.Column("granted_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_json", sa.JSON(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kid_id", "consent_type", name="uq_play_kid_consent"),
    )
    op.create_index("ix_play_kid_consents_kid", "play_kid_consents", ["kid_id"])

    op.create_table(
        "play_daily_screen_time",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("minutes_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "usage_date"),
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO play_games (
              id, display_name, game_type, hub_zone, is_public, requires_wallet,
              subject, grade_min, grade_max, sort_order, launch_url, meta_json
            )
            SELECT
              'memory_learn', 'Gà Nhớ bài', 'learning', 'learning', true, false,
              'memory', 1, 5, 3, '/game/memory-learn',
              '{"icon": "🃏", "route": "/game/memory-learn"}'
            WHERE NOT EXISTS (SELECT 1 FROM play_games WHERE id = 'memory_learn')
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE play_games SET
              hub_zone = 'reward', game_type = 'arcade', is_public = false,
              requires_wallet = true, subject = NULL,
              display_name = 'Lật bài nhớ', launch_url = '/game/memory'
            WHERE id = 'memory'
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE play_game_modes SET display_name = 'Gà Toán'
            WHERE id = 'math_blast:flappy' AND display_name LIKE '%Chim%'
            """
        )
    )


def downgrade() -> None:
    op.drop_table("play_daily_screen_time")
    op.drop_index("ix_play_kid_consents_kid", "play_kid_consents")
    op.drop_table("play_kid_consents")

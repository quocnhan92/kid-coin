"""English Shooter — catalog tables (themes, stages, items per GDD §8)

Revision ID: 012
Revises: 011
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONB = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "play_english_weapons",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("asset_id", sa.String(64), nullable=True),
        sa.Column("meta_json", JSONB(), server_default="{}", nullable=False),
    )
    op.create_index("ix_play_english_weapons_grade", "play_english_weapons", ["grade"])

    op.create_table(
        "play_english_bosses",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("asset_id", sa.String(64), nullable=True),
        sa.Column("intro_audio", sa.String(256), nullable=True),
        sa.Column("meta_json", JSONB(), server_default="{}", nullable=False),
    )

    op.create_table(
        "play_english_themes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("order_index", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("background_scene", sa.String(48), nullable=True),
        sa.Column("boss_id", sa.String(32), sa.ForeignKey("play_english_bosses.id"), nullable=True),
        sa.Column("content_pack_id", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("meta_json", JSONB(), server_default="{}", nullable=False),
    )
    op.create_index("ix_play_english_themes_grade", "play_english_themes", ["grade"])

    op.create_table(
        "play_english_stages",
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("theme_id", sa.String(32), sa.ForeignKey("play_english_themes.id"), nullable=False),
        sa.Column(
            "stage_type",
            sa.String(16),
            nullable=False,
        ),
        sa.Column("instruction_audio", sa.String(256), nullable=True),
        sa.Column("time_limit_seconds", sa.Integer(), nullable=True),
        sa.Column("speaking_required", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("min_confidence", sa.Numeric(4, 2), nullable=True),
        sa.Column("config_json", JSONB(), server_default="{}", nullable=False),
    )
    op.create_index("ix_play_english_stages_theme", "play_english_stages", ["theme_id"])

    op.create_table(
        "play_english_stage_items",
        sa.Column("id", sa.String(48), primary_key=True),
        sa.Column("stage_id", sa.String(48), sa.ForeignKey("play_english_stages.id"), nullable=False),
        sa.Column("item_type", sa.String(16), server_default="target", nullable=False),
        sa.Column("target_text", sa.Text(), nullable=False),
        sa.Column("audio_url", sa.String(256), nullable=True),
        sa.Column("visual_asset", sa.String(64), nullable=True),
        sa.Column("translation_vi", sa.String(200), nullable=True),
        sa.Column("options_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("order_index", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("skill_unit_id", sa.String(64), nullable=True),
    )
    op.create_index("ix_play_english_stage_items_stage", "play_english_stage_items", ["stage_id"])


def downgrade() -> None:
    op.drop_table("play_english_stage_items")
    op.drop_table("play_english_stages")
    op.drop_table("play_english_themes")
    op.drop_table("play_english_bosses")
    op.drop_table("play_english_weapons")

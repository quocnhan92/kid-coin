"""add play hub tables

Revision ID: 011
Revises: 010
Create Date: 2026-05-16

Math Blast / Play Hub — catalog, sessions, progress, analytics (MVP).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "play_games",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("game_type", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("current_release_id", sa.String(64), nullable=True),
        sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("meta_json", JSONB(), server_default="{}", nullable=False),
    )

    op.create_table(
        "play_content_packs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("locale", sa.String(8), server_default="vi-VN", nullable=False),
        sa.Column("grade_min", sa.SmallInteger(), nullable=False),
        sa.Column("grade_max", sa.SmallInteger(), nullable=False),
        sa.Column("manifest_version", sa.String(16), nullable=False),
        sa.Column("manifest_hash", sa.String(64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "play_game_modes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("game_id", sa.String(32), sa.ForeignKey("play_games.id"), nullable=False),
        sa.Column("mode_key", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("tracks_learning", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("content_pack_id", sa.String(64), nullable=True),
        sa.Column("config_json", JSONB(), server_default="{}", nullable=False),
    )
    op.create_index("ix_play_game_modes_game_id", "play_game_modes", ["game_id"])

    op.create_table(
        "play_skill_units",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("content_pack_id", sa.String(64), sa.ForeignKey("play_content_packs.id"), nullable=False),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("tags_json", JSONB(), server_default="[]", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_play_skill_units_pack", "play_skill_units", ["content_pack_id"])

    op.create_table(
        "play_skill_edges",
        sa.Column("from_skill_id", sa.String(64), sa.ForeignKey("play_skill_units.id"), primary_key=True),
        sa.Column("to_skill_id", sa.String(64), sa.ForeignKey("play_skill_units.id"), primary_key=True),
        sa.Column("edge_type", sa.String(8), nullable=False),
    )

    op.create_table(
        "play_levels",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("game_mode_id", sa.String(32), sa.ForeignKey("play_game_modes.id"), nullable=False),
        sa.Column("skill_unit_id", sa.String(64), sa.ForeignKey("play_skill_units.id"), nullable=True),
        sa.Column("grade", sa.SmallInteger(), nullable=True),
        sa.Column("chapter_id", sa.String(16), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("star_ref", sa.String(8), nullable=True),
        sa.Column("is_boss", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("prerequisite_level_ids", JSONB(), server_default="[]", nullable=False),
        sa.Column("sort_index", sa.Integer(), nullable=False),
        sa.Column("objective", sa.String(500), nullable=True),
    )
    op.create_index("ix_play_levels_mode", "play_levels", ["game_mode_id"])

    op.create_table(
        "play_game_releases",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("game_id", sa.String(32), sa.ForeignKey("play_games.id"), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )

    op.create_table(
        "play_profiles",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("family_id", UUID, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("target_grade", sa.SmallInteger(), nullable=True),
        sa.Column("birth_year", sa.SmallInteger(), nullable=True),
        sa.Column("active_content_pack_id", sa.String(64), server_default="vn_gdpt2018_candy_v1", nullable=False),
        sa.Column("preferences_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("parental_soft_cap_sessions_day", sa.SmallInteger(), server_default="6", nullable=False),
        sa.Column("parental_hard_cap_sessions_day", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_play_profiles_family", "play_profiles", ["family_id"])

    op.create_table(
        "play_level_progress",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("level_id", sa.String(16), sa.ForeignKey("play_levels.id"), primary_key=True),
        sa.Column("stars", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("best_accuracy", sa.Numeric(5, 4), nullable=True),
        sa.Column("best_avg_latency_ms", sa.Integer(), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("first_cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_unlocked", sa.Boolean(), server_default="false", nullable=False),
    )

    op.create_table(
        "play_skill_mastery_agg",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("skill_unit_id", sa.String(64), sa.ForeignKey("play_skill_units.id"), primary_key=True),
        sa.Column("rolling_accuracy", sa.Numeric(5, 4), server_default="0", nullable=False),
        sa.Column("rolling_avg_latency_ms", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mastery_score", sa.Numeric(5, 4), server_default="0", nullable=False),
        sa.Column("practice_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "play_user_game_stats",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("game_id", sa.String(32), sa.ForeignKey("play_games.id"), primary_key=True),
        sa.Column("game_mode_id", sa.String(32), primary_key=True, server_default=""),
        sa.Column("high_score", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("high_score_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_sessions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_play_time_s", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_questions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_correct", sa.Integer(), server_default="0", nullable=False),
        sa.Column("extra_json", JSONB(), server_default="{}", nullable=False),
    )

    op.create_table(
        "play_mode_progress",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("game_mode_id", sa.String(32), sa.ForeignKey("play_game_modes.id"), primary_key=True),
        sa.Column("tier_key", sa.String(8), primary_key=True),
        sa.Column("mastery_status", sa.String(16), server_default="locked", nullable=False),
        sa.Column("mastery_window_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mastered_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "play_sessions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", UUID, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("game_id", sa.String(32), nullable=False),
        sa.Column("game_mode_id", sa.String(32), nullable=True),
        sa.Column("status", sa.String(16), server_default="active", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("client_device_id", sa.String(64), nullable=True),
        sa.Column("content_pack_id", sa.String(64), nullable=True),
        sa.Column("manifest_hash", sa.String(64), nullable=True),
        sa.Column("release_id", sa.String(64), nullable=True),
    )
    op.create_index("ix_play_sessions_user_started", "play_sessions", ["user_id", "started_at"])
    op.create_index("ix_play_sessions_game_started", "play_sessions", ["game_id", "started_at"])
    op.create_index("ix_play_sessions_user_id", "play_sessions", ["user_id"])

    op.create_table(
        "play_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("session_id", UUID, sa.ForeignKey("play_sessions.id"), nullable=False),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("client_seq", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("skill_unit_id", sa.String(64), nullable=True),
        sa.Column("level_id", sa.String(16), nullable=True),
        sa.Column("item_id", sa.String(128), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("score_delta", sa.Integer(), nullable=True),
        sa.Column("context_json", JSONB(), server_default="{}", nullable=False),
        sa.UniqueConstraint("session_id", "client_seq", name="uq_play_events_session_seq"),
    )
    op.create_index("ix_play_events_session", "play_events", ["session_id"])
    op.create_index("ix_play_events_user_occurred", "play_events", ["user_id", "occurred_at"])

    op.create_table(
        "play_session_summaries",
        sa.Column("session_id", UUID, sa.ForeignKey("play_sessions.id"), primary_key=True),
        sa.Column("duration_s", sa.Numeric(8, 2), nullable=False),
        sa.Column("questions_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("correct_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("accuracy", sa.Numeric(5, 4), nullable=True),
        sa.Column("score", sa.BigInteger(), nullable=True),
        sa.Column("stars_earned", sa.SmallInteger(), nullable=True),
        sa.Column("level_id", sa.String(16), nullable=True),
        sa.Column("summary_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "play_idempotency_keys",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("endpoint", sa.String(64), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("response_json", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "play_daily_recommendations",
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("recommendation_date", sa.Date(), primary_key=True),
        sa.Column("items_json", JSONB(), server_default="[]", nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "play_parent_weekly_snapshots",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("family_id", UUID, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("report_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "week_start", name="uq_play_parent_weekly"),
    )
    op.create_index("ix_play_parent_weekly_family", "play_parent_weekly_snapshots", ["family_id"])

    op.create_table(
        "play_metrics_daily",
        sa.Column("metric_date", sa.Date(), primary_key=True),
        sa.Column("game_id", sa.String(32), sa.ForeignKey("play_games.id"), primary_key=True),
        sa.Column("game_mode_id", sa.String(32), primary_key=True, server_default=""),
        sa.Column("release_id", sa.String(64), primary_key=True, server_default=""),
        sa.Column("dau", sa.Integer(), server_default="0", nullable=False),
        sa.Column("new_users", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sessions_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("avg_session_duration_s", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("d1_retention", sa.Numeric(5, 4), nullable=True),
        sa.Column("d7_retention", sa.Numeric(5, 4), nullable=True),
        sa.Column("avg_accuracy", sa.Numeric(5, 4), nullable=True),
        sa.Column("paywall_views", sa.Integer(), nullable=True),
        sa.Column("trial_starts", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("play_metrics_daily")
    op.drop_table("play_parent_weekly_snapshots")
    op.drop_table("play_daily_recommendations")
    op.drop_table("play_idempotency_keys")
    op.drop_table("play_session_summaries")
    op.drop_table("play_events")
    op.drop_table("play_sessions")
    op.drop_table("play_mode_progress")
    op.drop_table("play_user_game_stats")
    op.drop_table("play_skill_mastery_agg")
    op.drop_table("play_level_progress")
    op.drop_table("play_profiles")
    op.drop_table("play_game_releases")
    op.drop_table("play_levels")
    op.drop_table("play_skill_edges")
    op.drop_table("play_skill_units")
    op.drop_table("play_game_modes")
    op.drop_table("play_content_packs")
    op.drop_table("play_games")

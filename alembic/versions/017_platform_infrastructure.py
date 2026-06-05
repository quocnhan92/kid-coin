"""Platform infrastructure: feature flags, domain events outbox, play game registry cols

Revision ID: 017_platform
Revises: 016_play_wallet
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "017_platform"
down_revision = "016_play_wallet"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("scope", sa.String(16), server_default="global", nullable=False),
        sa.Column("scope_value", sa.String(64), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("metadata_json", JSONB(), server_default="{}", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "scope", "scope_value", name="uq_feature_flag_scope"),
    )
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"])
    op.create_index("ix_feature_flags_scope", "feature_flags", ["scope", "scope_value"])

    op.create_table(
        "domain_events_outbox",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("aggregate_type", sa.String(32), nullable=True),
        sa.Column("aggregate_id", sa.String(64), nullable=True),
        sa.Column("payload_json", JSONB(), nullable=False),
        sa.Column("family_id", UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(16), server_default="pending", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_status_created", "domain_events_outbox", ["status", "created_at"])
    op.create_index("ix_outbox_event_type", "domain_events_outbox", ["event_type"])

    op.add_column(
        "play_games",
        sa.Column("ssr_template", sa.String(255), nullable=True),
    )
    op.add_column(
        "play_games",
        sa.Column("launch_url", sa.String(255), nullable=True),
    )
    op.add_column(
        "play_games",
        sa.Column("is_public", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "play_games",
        sa.Column(
            "min_client_version",
            sa.String(16),
            server_default="1.0.0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("play_games", "min_client_version")
    op.drop_column("play_games", "is_public")
    op.drop_column("play_games", "launch_url")
    op.drop_column("play_games", "ssr_template")
    op.drop_table("domain_events_outbox")
    op.drop_index("ix_feature_flags_scope", "feature_flags")
    op.drop_index("ix_feature_flags_key", "feature_flags")
    op.drop_table("feature_flags")

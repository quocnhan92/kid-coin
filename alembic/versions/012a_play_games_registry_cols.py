"""play_games registry columns — before ORM seed migrations (013+)

Revision ID: 012a_play_registry
Revises: 012
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "012a_play_registry"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return column in {c["name"] for c in insp.get_columns(table)}


def upgrade() -> None:
    cols = [
        ("ssr_template", sa.Column("ssr_template", sa.String(255), nullable=True)),
        ("launch_url", sa.Column("launch_url", sa.String(255), nullable=True)),
        (
            "is_public",
            sa.Column("is_public", sa.Boolean(), server_default="true", nullable=False),
        ),
        (
            "min_client_version",
            sa.Column(
                "min_client_version",
                sa.String(16),
                server_default="1.0.0",
                nullable=False,
            ),
        ),
        (
            "hub_zone",
            sa.Column(
                "hub_zone", sa.String(16), server_default="learning", nullable=False
            ),
        ),
        (
            "requires_wallet",
            sa.Column(
                "requires_wallet", sa.Boolean(), server_default="false", nullable=False
            ),
        ),
        ("subject", sa.Column("subject", sa.String(16), nullable=True)),
        (
            "grade_min",
            sa.Column("grade_min", sa.SmallInteger(), server_default="1", nullable=False),
        ),
        (
            "grade_max",
            sa.Column("grade_max", sa.SmallInteger(), server_default="5", nullable=False),
        ),
    ]
    for name, col in cols:
        if not _has_column("play_games", name):
            op.add_column("play_games", col)

    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {i["name"] for i in insp.get_indexes("play_games")}
    if "ix_play_games_hub_zone" not in indexes:
        op.create_index("ix_play_games_hub_zone", "play_games", ["hub_zone"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {i["name"] for i in insp.get_indexes("play_games")}
    if "ix_play_games_hub_zone" in indexes:
        op.drop_index("ix_play_games_hub_zone", table_name="play_games")
    for name in (
        "grade_max",
        "grade_min",
        "subject",
        "requires_wallet",
        "hub_zone",
        "min_client_version",
        "is_public",
        "launch_url",
        "ssr_template",
    ):
        if _has_column("play_games", name):
            op.drop_column("play_games", name)

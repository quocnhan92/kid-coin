"""Play hub zones: learning vs reward taxonomy

Revision ID: 018_play_hub_zones
Revises: 017_platform
"""
from alembic import op
import sqlalchemy as sa

revision = "018_play_hub_zones"
down_revision = "017_platform"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return column in {c["name"] for c in insp.get_columns(table)}


def upgrade() -> None:
    zone_cols = [
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
    for name, col in zone_cols:
        if not _has_column("play_games", name):
            op.add_column("play_games", col)

    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {i["name"] for i in insp.get_indexes("play_games")}
    if "ix_play_games_hub_zone" not in indexes:
        op.create_index("ix_play_games_hub_zone", "play_games", ["hub_zone"])

    conn = bind

    conn.execute(
        sa.text(
            """
            UPDATE play_games SET
              hub_zone = 'learning', game_type = 'learning', is_public = true,
              requires_wallet = false, subject = 'math', grade_min = 1, grade_max = 5,
              launch_url = COALESCE(launch_url, '/game/math-blast-v2')
            WHERE id = 'math_blast'
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE play_games SET
              hub_zone = 'learning', game_type = 'learning', is_public = true,
              requires_wallet = false, subject = 'english', grade_min = 1, grade_max = 5,
              launch_url = COALESCE(launch_url, '/game/english-shooter')
            WHERE id = 'english_shooter'
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE play_games SET
              hub_zone = 'learning', game_type = 'learning', is_public = true,
              requires_wallet = false, subject = 'math', grade_min = 1, grade_max = 5,
              launch_url = COALESCE(launch_url, '/game/english-shooter/math')
            WHERE id = 'english_math'
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE play_games SET
              hub_zone = 'learning', game_type = 'learning', is_public = true,
              requires_wallet = false, subject = 'memory', grade_min = 1, grade_max = 5,
              display_name = 'Lật bài học'
            WHERE id = 'memory'
            """
        )
    )
    for gid in ("snake", "2048", "flappy_classic"):
        conn.execute(
            sa.text(
                """
                UPDATE play_games SET
                  hub_zone = 'reward', game_type = 'arcade', is_public = false,
                  requires_wallet = true, subject = NULL, grade_min = 1, grade_max = 5
                WHERE id = :gid
                """
            ),
            {"gid": gid},
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {i["name"] for i in insp.get_indexes("play_games")}
    if "ix_play_games_hub_zone" in indexes:
        op.drop_index("ix_play_games_hub_zone", table_name="play_games")
    for name in ("grade_max", "grade_min", "subject", "requires_wallet", "hub_zone"):
        if _has_column("play_games", name):
            op.drop_column("play_games", name)

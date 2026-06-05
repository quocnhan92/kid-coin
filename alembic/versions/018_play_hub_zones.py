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


def upgrade() -> None:
    op.add_column(
        "play_games",
        sa.Column("hub_zone", sa.String(16), server_default="learning", nullable=False),
    )
    op.add_column(
        "play_games",
        sa.Column("requires_wallet", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "play_games",
        sa.Column("subject", sa.String(16), nullable=True),
    )
    op.add_column(
        "play_games",
        sa.Column("grade_min", sa.SmallInteger(), server_default="1", nullable=False),
    )
    op.add_column(
        "play_games",
        sa.Column("grade_max", sa.SmallInteger(), server_default="5", nullable=False),
    )
    op.create_index("ix_play_games_hub_zone", "play_games", ["hub_zone"])

    conn = op.get_bind()

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
    op.drop_index("ix_play_games_hub_zone", "play_games")
    op.drop_column("play_games", "grade_max")
    op.drop_column("play_games", "grade_min")
    op.drop_column("play_games", "subject")
    op.drop_column("play_games", "requires_wallet")
    op.drop_column("play_games", "hub_zone")

"""Play wallet ledger + english_math game (tách điểm toán EN/VN)

Revision ID: 016_play_wallet
Revises: 015_english_boss_subtopics_g123
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "016_play_wallet"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "play_kid_wallets",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("available_balance", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("accounts_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "play_wallet_ledger",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("account_code", sa.String(32), nullable=False),
        sa.Column("entry_type", sa.String(8), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("balance_after", sa.BigInteger(), nullable=False),
        sa.Column("ref_game_id", sa.String(32), nullable=True),
        sa.Column("ref_session_id", UUID(as_uuid=True), sa.ForeignKey("play_sessions.id"), nullable=True),
        sa.Column("ref_reward_game_id", sa.String(32), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_play_wallet_ledger_user_id", "play_wallet_ledger", ["user_id"])
    op.create_index("ix_play_wallet_ledger_created_at", "play_wallet_ledger", ["created_at"])

    conn = op.get_bind()
    exists = conn.execute(sa.text("SELECT 1 FROM play_games WHERE id = 'english_math'")).fetchone()
    if not exists:
        conn.execute(
            sa.text(
                """
                INSERT INTO play_games (id, display_name, game_type, is_active, sort_order, meta_json)
                VALUES (
                  'english_math', 'English Math', 'learning', true, 6,
                  '{"icon":"➕","route":"/game/english-shooter/math/v2","locale":"en"}'::jsonb
                )
                """
            )
        )
        for mode_id, mode_key, name in [
            ("english_math:candy", "candy", "Candy Map (EN)"),
            ("english_math:flappy", "flappy", "Math Bird (EN)"),
            ("english_math:arcade_free", "arcade_free", "Arcade (EN)"),
            ("english_math:arcade_class", "arcade_class", "Class Arcade (EN)"),
        ]:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO play_game_modes (id, game_id, mode_key, display_name, tracks_learning, config_json)
                    VALUES (:id, 'english_math', :key, :name, :track, '{}'::jsonb)
                    """
                ),
                {
                    "id": mode_id,
                    "key": mode_key,
                    "name": name,
                    "track": mode_key in ("candy", "flappy", "arcade_class"),
                },
            )
        conn.execute(
            sa.text(
                """
                INSERT INTO play_levels (
                  id, game_mode_id, skill_unit_id, grade, chapter_id, title,
                  star_ref, is_boss, prerequisite_level_ids, sort_index, objective
                )
                SELECT
                  'EN_' || id, 'english_math:candy', skill_unit_id, grade, chapter_id,
                  title, star_ref, is_boss, prerequisite_level_ids, sort_index, objective
                FROM play_levels
                WHERE game_mode_id = 'math_blast:candy'
                """
            )
        )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM play_levels WHERE game_mode_id = 'english_math:candy'"))
    op.execute(sa.text("DELETE FROM play_game_modes WHERE game_id = 'english_math'"))
    op.execute(sa.text("DELETE FROM play_games WHERE id = 'english_math'"))
    op.drop_index("ix_play_wallet_ledger_created_at", table_name="play_wallet_ledger")
    op.drop_index("ix_play_wallet_ledger_user_id", table_name="play_wallet_ledger")
    op.drop_table("play_wallet_ledger")
    op.drop_table("play_kid_wallets")

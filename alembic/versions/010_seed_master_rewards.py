"""seed master rewards data

Revision ID: 010
Revises: c0ac30523bed
Create Date: 2026-04-12 21:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = 'c0ac30523bed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MASTER_REWARDS = [
    ('Xem TV 30 phút', '📺', 50, 3, 18),
    ('Ăn kem', '🍦', 100, 3, 18),
    ('Thêm 15 phút chơi game', '🎮', 30, 5, 18),
    ('Đi công viên cuối tuần', '🎡', 500, 3, 15),
    ('Mua đồ chơi mới (nhỏ)', '🧸', 300, 3, 12),
    ('Được thức khuya thêm 30 phút', '🌃', 100, 7, 18),
    ('Miễn làm việc nhà 1 ngày', '💆', 200, 6, 18),
    ('Được chọn món cho bữa tối', '🍕', 50, 3, 18),
    ('Đi xem phim rạp', '🍿', 600, 6, 18),
    ('Đồ uống yêu thích (Trà sữa/Nước ngọt)', '🥤', 80, 5, 18),
]

def upgrade() -> None:
    conn = op.get_bind()
    for name, icon_url, suggested_cost, min_age, max_age in MASTER_REWARDS:
        conn.execute(
            text("""
                INSERT INTO master_rewards (name, icon_url, suggested_cost, min_age, max_age)
                SELECT :name, :icon_url, :suggested_cost, :min_age, :max_age
                WHERE NOT EXISTS (
                    SELECT 1 FROM master_rewards WHERE name = :name
                )
            """),
            {
                "name": name, 
                "icon_url": icon_url, 
                "suggested_cost": suggested_cost,
                "min_age": min_age,
                "max_age": max_age
            }
        )

def downgrade() -> None:
    conn = op.get_bind()
    names = [r[0] for r in MASTER_REWARDS]
    conn.execute(
        text("DELETE FROM master_rewards WHERE name = ANY(:names)"),
        {"names": names}
    )

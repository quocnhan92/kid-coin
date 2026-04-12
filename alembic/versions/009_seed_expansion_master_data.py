"""seed expansion master data

Revision ID: 009
Revises: 008
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


USER_LEVELS = [
    (1, 'Người mới', 0, 'Sẵn lòng bắt đầu cuộc hành trình.'),
    (2, 'Thợ học việc', 100, 'Bắt đầu làm quen với các công việc nhỏ.'),
    (3, 'Chiến binh', 300, 'Mạnh mẽ và đầy nhiệt huyết trong công việc.'),
    (4, 'Thủ lĩnh trẻ', 600, 'Biết cách tự sắp xếp kế hoạch cho bản thân.'),
    (5, 'Hiệp sĩ nhí', 1000, 'Luôn bảo vệ và giúp đỡ gia đình.'),
    (6, 'Pháp sư chăm chỉ', 1500, 'Biến những công việc khó khăn trở nên dễ dàng.'),
    (7, 'Anh hùng gia đình', 2100, 'Một tấm gương sáng cho mọi người.'),
    (8, 'Bậc thầy tự lập', 2800, 'Làm chủ hoàn toàn các kỹ năng cá nhân.'),
    (9, 'Đại sứ nhí', 3600, 'Lan tỏa niềm vui và sự giúp đỡ đến xã hội.'),
    (10, 'Huyền thoại KidCoin', 4500, 'Đẳng cấp cao nhất, một biểu tượng thật sự.'),
]

AVATAR_ITEMS = [
    # Frames (Khung ảnh)
    ('Khung gỗ mộc mạc', 'FRAME', 50, 'https://cdn-icons-png.flaticon.com/512/1048/1048953.png'),
    ('Khung bạc sáng', 'FRAME', 200, 'https://cdn-icons-png.flaticon.com/512/2583/2583277.png'),
    ('Khung vàng hoàng gia', 'FRAME', 500, 'https://cdn-icons-png.flaticon.com/512/2583/2583264.png'),
    ('Khung Neon điện tử', 'FRAME', 1000, 'https://cdn-icons-png.flaticon.com/512/1154/1154425.png'),
    ('Khung Cầu vồng kỳ ảo', 'FRAME', 2000, 'https://cdn-icons-png.flaticon.com/512/2619/2619245.png'),

    # Badges (Huy hiệu)
    ('Huy hiệu Chăm chỉ', 'BADGE', 100, 'https://cdn-icons-png.flaticon.com/512/1904/1904425.png'),
    ('Huy hiệu Tiết kiệm', 'BADGE', 150, 'https://cdn-icons-png.flaticon.com/512/1904/1904437.png'),
    ('Huy hiệu Giúp đỡ', 'BADGE', 200, 'https://cdn-icons-png.flaticon.com/512/1904/1904481.png'),
    ('Huy hiệu Sáng tạo', 'BADGE', 300, 'https://cdn-icons-png.flaticon.com/512/1904/1904515.png'),
    ('Huy hiệu Dũng cảm', 'BADGE', 500, 'https://cdn-icons-png.flaticon.com/512/1904/1904533.png'),

    # Backgrounds (Nền)
    ('Bầu trời xanh ngắt', 'BACKGROUND', 100, 'https://cdn-icons-png.flaticon.com/512/2675/2675840.png'),
    ('Nắng vàng rực rỡ', 'BACKGROUND', 150, 'https://cdn-icons-png.flaticon.com/512/2675/2675848.png'),
    ('Đêm huyền bí', 'BACKGROUND', 250, 'https://cdn-icons-png.flaticon.com/512/2675/2675878.png'),
    ('Rừng xanh đại ngàn', 'BACKGROUND', 400, 'https://cdn-icons-png.flaticon.com/512/2675/2675883.png'),
    ('Vũ trụ bao la', 'BACKGROUND', 800, 'https://cdn-icons-png.flaticon.com/512/2675/2675900.png'),

    # Accessories (Phụ kiện)
    ('Khăn quàng đỏ thắm', 'ACCESSORY', 50, 'https://cdn-icons-png.flaticon.com/512/2533/2533552.png'),
    ('Kính tri thức', 'ACCESSORY', 150, 'https://cdn-icons-png.flaticon.com/512/2533/2533560.png'),
    ('Áo choàng siêu nhân', 'ACCESSORY', 300, 'https://cdn-icons-png.flaticon.com/512/2533/2533580.png'),
    ('Vương miện lấp lánh', 'ACCESSORY', 1000, 'https://cdn-icons-png.flaticon.com/512/2533/2533600.png'),
    ('Gậy phép thuật', 'ACCESSORY', 2000, 'https://cdn-icons-png.flaticon.com/512/2533/2533610.png'),
]


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Fix Schema mismatch from 003
    # Fix user_levels
    op.execute(text("ALTER TABLE user_levels RENAME COLUMN title TO name"))
    op.execute(text("ALTER TABLE user_levels RENAME COLUMN xp_required TO min_xp"))
    op.execute(text("ALTER TABLE user_levels ADD COLUMN IF NOT EXISTS description VARCHAR(500)"))
    op.execute(text("ALTER TABLE user_levels DROP COLUMN IF EXISTS icon_url"))

    # Fix avatar_items
    op.execute(text("ALTER TABLE avatar_items RENAME COLUMN icon_url TO image_url"))
    op.execute(text("ALTER TABLE avatar_items RENAME COLUMN price_coin TO price_coins"))

    # 2. Seed User Levels
    for level, name, min_xp, description in USER_LEVELS:
        conn.execute(
            text("""
                INSERT INTO user_levels (level, name, min_xp, description)
                VALUES (:level, :name, :min_xp, :description)
                ON CONFLICT (level) DO UPDATE SET
                    name = EXCLUDED.name,
                    min_xp = EXCLUDED.min_xp,
                    description = EXCLUDED.description
            """),
            {"level": level, "name": name, "min_xp": min_xp, "description": description}
        )

    # Seed Avatar Items
    for name, item_type, price_coins, image_url in AVATAR_ITEMS:
        conn.execute(
            text("""
                INSERT INTO avatar_items (name, item_type, price_coins, image_url, is_active)
                SELECT :name, :item_type, :price_coins, :image_url, true
                WHERE NOT EXISTS (
                    SELECT 1 FROM avatar_items WHERE name = :name AND item_type = :item_type
                )
            """),
            {"name": name, "item_type": item_type, "price_coins": price_coins, "image_url": image_url}
        )


def downgrade() -> None:
    conn = op.get_bind()
    
    # Xóa avatar items theo tên
    item_names = [item[0] for item in AVATAR_ITEMS]
    conn.execute(
        text("DELETE FROM avatar_items WHERE name = ANY(:names)"),
        {"names": item_names}
    )

    # Xóa user levels
    conn.execute(text("DELETE FROM user_levels"))

"""seed master tasks data

Revision ID: 002
Revises: 001
Create Date: 2026-04-10 00:00:00.000000

Seed 100 master tasks across 5 categories:
- Cá nhân (20 tasks)
- Việc nhà - Hỗ trợ gia đình (20 tasks)
- Việc nhà - Dọn dẹp (20 tasks)
- Học tập (20 tasks)
- Xã hội (20 tasks)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Map từ tiếng Việt → giá trị thực tế trong PostgreSQL ENUM (Đã chuẩn hóa sang English Keys)
CATEGORY_MAP = {
    'Cá nhân':  'PERSONAL',
    'Việc nhà': 'CHORE',
    'Học tập':  'STUDY',
    'Xã hội':   'SOCIAL',
}

VERIFICATION_MAP = {
    'Tự động duyệt':             'AUTO_APPROVE',
    'Cần chụp ảnh':              'REQUIRE_PHOTO',
    'Bố mẹ kiểm tra trực tiếp': 'REQUIRE_PARENT_CHECK',
}

# 100 master tasks: (name, icon_url, suggested_value, category, verification_type)
MASTER_TASKS = [
    # ── NHÓM 1: CÁ NHÂN & ĂN UỐNG (20) ──────────────────────────────────────
    ('Tự xúc ăn ngoan trong 30 phút',        '🍽️', 15, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Không bỏ mứa đồ ăn',                   '🍽️', 10, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Thử một món rau mới',                   '🥦',  15, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Uống sữa không cần nhắc',               '🥛',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Không xem TV/iPad lúc ăn',              '🚫',  10, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Tự đánh răng buổi sáng',                '🪥',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Tự đánh răng buổi tối',                 '🪥',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Gấp chăn gối sau khi dậy',              '🛏️', 10, 'Cá nhân',  'Cần chụp ảnh'),
    ('Tự giác đi ngủ đúng giờ',               '🛌',  10, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Tự chuẩn bị quần áo mai mặc',           '👕',   5, 'Cá nhân',  'Cần chụp ảnh'),
    ('Tự tắm rửa sạch sẽ',                    '🛁',  10, 'Cá nhân',  'Tự động duyệt'),
    ('Cất giày dép lên kệ ngay ngắn',         '👟',   5, 'Cá nhân',  'Cần chụp ảnh'),
    ('Tự mặc quần áo',                        '👕',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Uống đủ 1 lít nước mỗi ngày',           '💧',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Rửa tay xà phòng trước khi ăn',         '🧼',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Chải tóc gọn gàng',                     '✨',   5, 'Cá nhân',  'Tự động duyệt'),
    ('Tự dọn bát đĩa của mình',               '🍽️',  5, 'Cá nhân',  'Cần chụp ảnh'),
    ('Tự cắt/nhờ bố mẹ cắt móng tay',        '💅',   5, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Ngủ trưa ngoan',                        '😴',  10, 'Cá nhân',  'Bố mẹ kiểm tra trực tiếp'),
    ('Rửa mặt sạch sẽ',                       '🧽',   5, 'Cá nhân',  'Tự động duyệt'),

    # ── NHÓM 2: HỖ TRỢ GIA ĐÌNH (20) ────────────────────────────────────────
    ('Lấy bỉm/tã giúp mẹ',                   '👶',  10, 'Việc nhà', 'Tự động duyệt'),
    ('Lấy khăn ướt/khăn giấy cho em',         '🧻',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Chơi ú òa/dỗ em bé',                    '🧸',  15, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Trông em 10 phút',                      '⏱️', 20, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Lấy nước cho bố/mẹ',                    '🥛',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Bóp vai/đấm lưng cho gia đình',         '💆',  10, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Phụ mẹ nhặt rau',                       '🥬',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Xách phụ đồ nhẹ khi đi siêu thị',      '🛍️', 10, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Ra mở cửa khi có người gọi',            '🚪',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Tắt điện/quạt khi ra khỏi phòng',      '💡',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Cất gọn đồ chơi của em bé',             '🧸',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Đọc truyện/Hát cho em nghe',            '📖',  15, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Phụ mẹ phơi đồ nhỏ',                   '👕',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Rút quần áo khô vào nhà',               '🧺',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lấy tăm/khăn giấy sau bữa ăn',         '🧻',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Lau bàn ăn sau khi dùng bữa',           '✨',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Cất gọn điều hòa/TV remote',            '📱',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Gấp đồ lót/tất của mình',               '🧦',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Mời người lớn ăn cơm',                  '🗣️',  5, 'Việc nhà', 'Bố mẹ kiểm tra trực tiếp'),
    ('Phụ bố dọn đồ nghề',                    '🧰',  10, 'Việc nhà', 'Cần chụp ảnh'),

    # ── NHÓM 3: VIỆC NHÀ - DỌN DẸP (20) ─────────────────────────────────────
    ('Quét nhà sạch sẽ',                      '🧹',  15, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lau sàn nhà',                           '🧹',  20, 'Việc nhà', 'Cần chụp ảnh'),
    ('Đổ rác đúng nơi quy định',              '🗑️', 10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Bọc túi rác mới vào thùng',             '🗑️',  5, 'Việc nhà', 'Tự động duyệt'),
    ('Tưới cây ngoài ban công',               '🪴',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Cho thú cưng ăn',                       '🐕',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lau bụi kệ sách/tủ TV',                 '🧽',  15, 'Việc nhà', 'Cần chụp ảnh'),
    ('Sắp xếp lại tủ quần áo',               '🚪',  15, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lau gương trong phòng tắm',             '✨',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Xếp lại kệ giày dép cả nhà',           '👟',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Dọn dẹp đồ chơi của mình',             '🧸',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Gom quần áo bẩn vào rổ',               '🧺',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Sắp xếp gọn gối sofa',                 '🛋️',  5, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lau tay nắm cửa',                      '🚪',  10, 'Việc nhà', 'Cần chụp ảnh'),
    ('Phân loại rác',                        '♻️',  15, 'Việc nhà', 'Cần chụp ảnh'),
    ('Cất sách báo vào đúng chỗ',            '📚',   5, 'Việc nhà', 'Cần chụp ảnh'),
    ('Quét dọn mạng nhện góc nhà',           '🧹',  15, 'Việc nhà', 'Cần chụp ảnh'),
    ('Lau công tắc đèn',                     '💡',  10, 'Việc nhà', 'Tự động duyệt'),
    ('Thay giấy vệ sinh mới',                '🧻',   5, 'Việc nhà', 'Tự động duyệt'),
    ('Rửa cốc/tách của mình',                '☕',  10, 'Việc nhà', 'Cần chụp ảnh'),

    # ── NHÓM 4: HỌC TẬP & RÈN LUYỆN (20) ────────────────────────────────────
    ('Tự giác ngồi vào bàn học',             '📚',  15, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Tự soạn cặp sách ngày mai',            '🎒',  10, 'Học tập',  'Cần chụp ảnh'),
    ('Làm xong bài tập về nhà',              '📝',  20, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Luyện viết chữ đẹp',                   '✍️', 15, 'Học tập',  'Cần chụp ảnh'),
    ('Đọc sách/truyện 20 phút',              '📖',  20, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Học 5 từ vựng tiếng Anh',              '🔤',  15, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Tự bọc sách/dán nhãn vở',              '🏷️', 10, 'Học tập',  'Cần chụp ảnh'),
    ('Dọn rác trên bàn học',                 '🗑️',  5, 'Học tập',  'Cần chụp ảnh'),
    ('Vẽ một bức tranh sáng tạo',            '🎨',  10, 'Học tập',  'Cần chụp ảnh'),
    ('Tập thể dục buổi sáng 10 phút',        '🏃',  15, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Nhảy dây 50 cái',                      '🪢',  15, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Chơi thể thao ngoài trời',             '⚽',  20, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Không dùng điện thoại cả ngày',        '📵',  30, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Ôn lại bài cũ',                        '📚',  15, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Giải một câu đố khó',                  '🧩',  10, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Kiểm tra lại hộp bút',                 '✏️',  5, 'Học tập',  'Tự động duyệt'),
    ('Kể một điều vui ở trường',             '😄',   5, 'Học tập',  'Bố mẹ kiểm tra trực tiếp'),
    ('Tập viết nhật ký',                     '📓',  10, 'Học tập',  'Cần chụp ảnh'),
    ('Hoàn thành bài tập thủ công',          '✂️', 15, 'Học tập',  'Cần chụp ảnh'),
    ('Chơi Lego/Xếp hình',                   '🧱',  10, 'Học tập',  'Cần chụp ảnh'),

    # ── NHÓM 5: GIAO TIẾP & CỘNG ĐỒNG (20) ──────────────────────────────────
    ('Chào hỏi lễ phép người lớn',           '🙇',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Nói Cảm ơn',                           '🙏',   5, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Nói Xin lỗi',                          '😔',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Chia sẻ đồ chơi với bạn/em',           '🤝',  15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Bấm giữ thang máy',                    '🛗',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Bỏ rác đúng thùng rác công cộng',      '🗑️', 10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Không làm ồn nơi công cộng',           '🤫',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Giúp đỡ bạn bè ở lớp',                '🤝',  15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Nói lời yêu thương',                   '❤️', 10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Quyên góp đồ chơi/quần áo cũ',        '🎁',  20, 'Xã hội',   'Cần chụp ảnh'),
    ('Làm thiệp tặng sinh nhật bạn',         '💌',  15, 'Xã hội',   'Cần chụp ảnh'),
    ('Gọi điện hỏi thăm ông bà',             '☎️', 15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Nhặt rác ở sân chơi chung',            '♻️',  15, 'Xã hội',   'Cần chụp ảnh'),
    ('Khen ngợi một ai đó',                  '👍',   5, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Không cãi lời người lớn',              '🤐',  15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Nhường ghế cho em nhỏ/người già',      '💺',  20, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Chào bác bảo vệ/lao công',             '👋',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Tuân thủ luật giao thông',             '🚦',  10, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Giữ trật tự khi người lớn nói chuyện', '🤫',  15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
    ('Giúp một người lạ (có bố mẹ)',         '🦸',  15, 'Xã hội',   'Bố mẹ kiểm tra trực tiếp'),
]


def upgrade() -> None:
    conn = op.get_bind()

    for name, icon_url, suggested_value, category_vi, verification_vi in MASTER_TASKS:
        category = CATEGORY_MAP[category_vi]
        verification_type = VERIFICATION_MAP[verification_vi]

        conn.execute(
            text("""
                INSERT INTO master_tasks (name, icon_url, suggested_value, category, verification_type)
                SELECT :name, :icon_url, :suggested_value, :category, :verification_type
                WHERE NOT EXISTS (
                    SELECT 1 FROM master_tasks WHERE name = :name
                )
            """),
            {
                "name": name,
                "icon_url": icon_url,
                "suggested_value": suggested_value,
                "category": category,
                "verification_type": verification_type,
            }
        )


def downgrade() -> None:
    conn = op.get_bind()
    names = [t[0] for t in MASTER_TASKS]
    # Xóa theo từng tên để tránh xóa nhầm data user tự tạo
    for name in names:
        conn.execute(
            text("DELETE FROM master_tasks WHERE name = :name"),
            {"name": name}
        )

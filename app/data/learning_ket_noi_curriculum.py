"""
Chương trình SGK Kết nối tri thức với cuộc sống — lớp 1→5.
Khung chủ đề/bài theo phân phối chương trình (tham chiếu vietjack.com / SGK NXBGD).
Nội dung quiz/read do hệ thống sinh — không sao chép bài tập có bản quyền.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.data.learning_ket_noi_content import build_lesson_content, lesson_content_type
from app.models.learning import LearningChapter, LearningLesson, LearningSubject

TEXTBOOK = "ket_noi_tri_thuc"

# grade -> colors
GRADE_STYLE: Dict[int, Dict[str, str]] = {
    1: {"color_primary": "#E85D24", "color_bg": "#FAECE7", "color_dark": "#993C1D"},
    2: {"color_primary": "#D4537E", "color_bg": "#FBEAF0", "color_dark": "#72243E"},
    3: {"color_primary": "#639922", "color_bg": "#EAF3DE", "color_dark": "#27500A"},
    4: {"color_primary": "#185FA5", "color_bg": "#E6F1FB", "color_dark": "#0C447C"},
    5: {"color_primary": "#7F77DD", "color_bg": "#EEEDFE", "color_dark": "#3C3489"},
}

# (slug, name, icon, description, sort)
SUBJECT_TEMPLATES: Dict[int, List[Tuple[str, str, str, str, int]]] = {
    1: [
        ("tieng-viet", "Tiếng Việt", "📖", "Đọc, viết chữ cái và từ đơn giản", 1),
        ("toan", "Toán", "📐", "Đếm, cộng trừ trong phạm vi 100", 2),
        ("dao-duc", "Đạo đức", "🌱", "Bài học về tính tốt và lễ phép", 3),
        ("tn-xh", "Tự nhiên & Xã hội", "🌍", "Thế giới xung quanh bé", 4),
        ("the-chat", "Thể chất", "⚽", "Vận động và trò chơi vui", 5),
        ("nghe-thuat", "Nghệ thuật", "🎨", "Âm nhạc và mỹ thuật", 6),
        ("hdtn", "Hoạt động trải nghiệm", "🌟", "Khám phá và sáng tạo", 7),
    ],
    2: [
        ("tieng-viet", "Tiếng Việt", "📖", "Đọc truyện và viết câu", 1),
        ("toan", "Toán", "📐", "Số đến 1000 và hình học cơ bản", 2),
        ("dao-duc", "Đạo đức", "🌱", "Tình bạn, lòng biết ơn", 3),
        ("tn-xh", "Tự nhiên & Xã hội", "🌍", "Gia đình, trường học, môi trường", 4),
        ("the-chat", "Thể chất", "⚽", "Thể dục và trò chơi nhóm", 5),
        ("nghe-thuat", "Nghệ thuật", "🎨", "Vẽ và hát các bài quen", 6),
        ("hdtn", "Hoạt động trải nghiệm", "🌟", "Tự phục vụ và hợp tác", 7),
    ],
    3: [
        ("tieng-viet", "Tiếng Việt", "📖", "Đọc hiểu và viết đoạn văn", 1),
        ("toan", "Toán", "📐", "Nhân chia và đo lường", 2),
        ("dao-duc", "Đạo đức", "🌱", "Trung thực và trách nhiệm", 3),
        ("tn-xh", "Tự nhiên & Xã hội", "🌍", "Cơ thể người và xã hội", 4),
        ("ngoai-ngu", "Ngoại ngữ 1", "🌐", "Tiếng Anh cơ bản", 5),
        ("tin-hoc", "Tin học & Công nghệ", "💻", "Máy tính và an toàn mạng", 6),
        ("the-chat", "Thể chất", "⚽", "Kỹ năng vận động", 7),
        ("nghe-thuat", "Nghệ thuật", "🎨", "Âm nhạc và mỹ thuật", 8),
        ("hdtn", "Hoạt động trải nghiệm", "🌟", "Dự án cộng đồng nhỏ", 9),
    ],
    4: [
        ("tieng-viet", "Tiếng Việt", "📖", "Đọc hiểu sâu và tập làm văn", 1),
        ("toan", "Toán", "📐", "Phân số, diện tích, số liệu", 2),
        ("dao-duc", "Đạo đức", "🌱", "Công dân tốt và bảo vệ môi trường", 3),
        ("lich-su-dia-ly", "Lịch sử & Địa lý", "🗺️", "Lịch sử Việt Nam và địa lý", 4),
        ("khoa-hoc", "Khoa học", "🔬", "Vật chất, năng lượng, sinh vật", 5),
        ("ngoai-ngu", "Ngoại ngữ 1", "🌐", "Tiếng Anh giao tiếp cơ bản", 6),
        ("tin-hoc", "Tin học & Công nghệ", "💻", "Xử lý thông tin và lập trình", 7),
        ("the-chat", "Thể chất", "⚽", "Thể dục và thể thao", 8),
        ("nghe-thuat", "Nghệ thuật", "🎨", "Âm nhạc và mỹ thuật", 9),
        ("hdtn", "Hoạt động trải nghiệm", "🌟", "Hướng nghiệp sớm", 10),
    ],
    5: [
        ("tieng-viet", "Tiếng Việt", "📖", "Văn học và kỹ năng viết", 1),
        ("toan", "Toán", "📐", "Tỉ lệ, thể tích, thống kê", 2),
        ("dao-duc", "Đạo đức", "🌱", "Tự trọng và quyền trẻ em", 3),
        ("lich-su-dia-ly", "Lịch sử & Địa lý", "🗺️", "Đất nước và thế giới", 4),
        ("khoa-hoc", "Khoa học", "🔬", "Sinh học, vật lý, hóa học cơ bản", 5),
        ("ngoai-ngu", "Ngoại ngữ 1", "🌐", "Tiếng Anh nâng cao", 6),
        ("tin-hoc", "Tin học & Công nghệ", "💻", "Lập trình và ứng dụng", 7),
        ("the-chat", "Thể chất", "⚽", "Thể dục và sức khỏe", 8),
        ("nghe-thuat", "Nghệ thuật", "🎨", "Âm nhạc và mỹ thuật", 9),
        ("hdtn", "Hoạt động trải nghiệm", "🌟", "Lãnh đạo và sáng tạo", 10),
    ],
}

# Chapter = (tên chủ đề, mô tả, mã SGK, [bài micro theo tuần])
ChapterDef = Tuple[str, str, str, List[str]]

MATH_G1: List[ChapterDef] = [
    ("Chủ đề 1: Các số từ 0 đến 10", "Bài 1–6 · HK1", "G1-TOAN-CD1", ["Các số 0–5", "Các số 6–10", "So sánh số"]),
    ("Chủ đề 2: Làm quen hình phẳng", "Bài 7–9", "G1-TOAN-CD2", ["Hình tròn, vuông", "Hình tam giác", "Ghép hình"]),
    ("Chủ đề 3: Cộng trừ trong 10", "Bài 10–13", "G1-TOAN-CD3", ["Phép cộng", "Phép trừ", "Luyện tập"]),
    ("Chủ đề 4: Làm quen hình khối", "Bài 14–16", "G1-TOAN-CD4", ["Khối lập phương", "Khối hộp", "Xếp khối"]),
    ("Chủ đề 5: Ôn tập HK1", "Bài 17–20", "G1-TOAN-CD5", ["Ôn số đến 10", "Ôn cộng trừ", "Kiểm tra HK1"]),
    ("Chủ đề 6: Các số đến 100", "Bài 21–24 · HK2", "G1-TOAN-CD6", ["Số đến 20", "Số đến 100", "So sánh số"]),
    ("Chủ đề 7: Độ dài và đo độ dài", "Bài 25–28", "G1-TOAN-CD7", ["So sánh độ dài", "Đo bằng thước", "Luyện tập"]),
    ("Chủ đề 8: Cộng trừ trong 100", "Bài 29–33", "G1-TOAN-CD8", ["Cộng không nhớ", "Trừ không nhớ", "Giải toán"]),
    ("Chủ đề 9: Thời gian, giờ và lịch", "Bài 34–37", "G1-TOAN-CD9", ["Ngày, tháng", "Giờ trên đồng hồ", "Lịch tuần"]),
    ("Chủ đề 10: Ôn tập cuối năm", "Bài 38–41", "G1-TOAN-CD10", ["Ôn số học", "Ôn hình học", "Kiểm tra cuối năm"]),
]

MATH_G2: List[ChapterDef] = [
    ("Chủ đề 1: Ôn tập số đến 100", "HK1", "G2-TOAN-CD1", ["Ôn số đến 100", "So sánh số", "Luyện tập"]),
    ("Chủ đề 2: Số có ba chữ số", "HK1", "G2-TOAN-CD2", ["Đọc viết số", "So sánh số", "Thứ tự số"]),
    ("Chủ đề 3: Cộng trừ có nhớ", "HK1", "G2-TOAN-CD3", ["Cộng có nhớ", "Trừ có nhớ", "Giải toán"]),
    ("Chủ đề 4: Hình học phẳng", "HK1", "G2-TOAN-CD4", ["Đường thẳng", "Hình tứ giác", "Luyện tập"]),
    ("Chủ đề 5: Ôn tập HK1", "HK1", "G2-TOAN-CD5", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
    ("Chủ đề 6: Phép nhân và chia", "HK2", "G2-TOAN-CD6", ["Làm quen nhân", "Làm quen chia", "Bảng nhân 2,3"]),
    ("Chủ đề 7: Chia sẻ đều", "HK2", "G2-TOAN-CD7", ["Chia đều", "Phép chia", "Luyện tập"]),
    ("Chủ đề 8: Số đối và liền kề", "HK2", "G2-TOAN-CD8", ["Số đối", "Liền trước sau", "Luyện tập"]),
    ("Chủ đề 9: Đơn vị đo", "HK2", "G2-TOAN-CD9", ["Đo độ dài", "Đo khối lượng", "Luyện tập"]),
    ("Chủ đề 10: Ôn tập cuối năm", "HK2", "G2-TOAN-CD10", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
]

MATH_G3: List[ChapterDef] = [
    ("Chủ đề 1: Ôn tập số đến 1000", "HK1", "G3-TOAN-CD1", ["Ôn số", "So sánh", "Luyện tập"]),
    ("Chủ đề 2: Phép nhân", "HK1", "G3-TOAN-CD2", ["Nhân có nhớ", "Bảng nhân", "Giải toán"]),
    ("Chủ đề 3: Phép chia", "HK1", "G3-TOAN-CD3", ["Chia hết", "Chia có dư", "Luyện tập"]),
    ("Chủ đề 4: Hình học", "HK1", "G3-TOAN-CD4", ["Chu vi", "Diện tích", "Luyện tập"]),
    ("Chủ đề 5: Ôn tập HK1", "HK1", "G3-TOAN-CD5", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
    ("Chủ đề 6: Số có bốn chữ số", "HK2", "G3-TOAN-CD6", ["Đọc viết số", "So sánh", "Luyện tập"]),
    ("Chủ đề 7: Phân số ban đầu", "HK2", "G3-TOAN-CD7", ["Làm quen phân số", "So sánh", "Luyện tập"]),
    ("Chủ đề 8: Đo lường", "HK2", "G3-TOAN-CD8", ["Đơn vị đo", "Đổi đơn vị", "Luyện tập"]),
    ("Chủ đề 9: Thời gian", "HK2", "G3-TOAN-CD9", ["Ngày giờ", "Lịch", "Luyện tập"]),
    ("Chủ đề 10: Ôn tập cuối năm", "HK2", "G3-TOAN-CD10", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
]

MATH_G4: List[ChapterDef] = [
    ("Chủ đề 1: Số tự nhiên", "HK1", "G4-TOAN-CD1", ["Số lớn", "Làm tròn", "Luyện tập"]),
    ("Chủ đề 2: Phép cộng trừ", "HK1", "G4-TOAN-CD2", ["Cộng trừ lớn", "Giải toán", "Luyện tập"]),
    ("Chủ đề 3: Phép nhân chia", "HK1", "G4-TOAN-CD3", ["Nhân chia", "Giải toán", "Luyện tập"]),
    ("Chủ đề 4: Phân số", "HK1", "G4-TOAN-CD4", ["Phân số", "So sánh", "Luyện tập"]),
    ("Chủ đề 5: Ôn tập HK1", "HK1", "G4-TOAN-CD5", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
    ("Chủ đề 6: Diện tích hình", "HK2", "G4-TOAN-CD6", ["Hình chữ nhật", "Hình vuông", "Luyện tập"]),
    ("Chủ đề 7: Góc và hình", "HK2", "G4-TOAN-CD7", ["Góc vuông", "Hình tam giác", "Luyện tập"]),
    ("Chủ đề 8: Số thập phân", "HK2", "G4-TOAN-CD8", ["Làm quen", "So sánh", "Luyện tập"]),
    ("Chủ đề 9: Số liệu", "HK2", "G4-TOAN-CD9", ["Bảng số liệu", "Biểu đồ", "Luyện tập"]),
    ("Chủ đề 10: Ôn tập cuối năm", "HK2", "G4-TOAN-CD10", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
]

MATH_G5: List[ChapterDef] = [
    ("Chủ đề 1: Ôn tập số tự nhiên", "HK1", "G5-TOAN-CD1", ["Ôn số", "Quy tắc", "Luyện tập"]),
    ("Chủ đề 2: Phân số", "HK1", "G5-TOAN-CD2", ["Cộng trừ PS", "Nhân chia PS", "Luyện tập"]),
    ("Chủ đề 3: Số thập phân", "HK1", "G5-TOAN-CD3", ["Cộng trừ STP", "Nhân chia STP", "Luyện tập"]),
    ("Chủ đề 4: Tỉ lệ phần trăm", "HK1", "G5-TOAN-CD4", ["Tỉ lệ", "Phần trăm", "Luyện tập"]),
    ("Chủ đề 5: Ôn tập HK1", "HK1", "G5-TOAN-CD5", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
    ("Chủ đề 6: Diện tích thể tích", "HK2", "G5-TOAN-CD6", ["Diện tích", "Thể tích", "Luyện tập"]),
    ("Chủ đề 7: Hình học không gian", "HK2", "G5-TOAN-CD7", ["Hình hộp", "Hình lập phương", "Luyện tập"]),
    ("Chủ đề 8: Thống kê", "HK2", "G5-TOAN-CD8", ["Trung bình", "Biểu đồ", "Luyện tập"]),
    ("Chủ đề 9: Ôn tập tổng hợp", "HK2", "G5-TOAN-CD9", ["Ôn số", "Ôn hình", "Luyện tập"]),
    ("Chủ đề 10: Ôn tập cuối năm", "HK2", "G5-TOAN-CD10", ["Ôn tập", "Luyện tập", "Kiểm tra"]),
]

MATH_BY_GRADE = {1: MATH_G1, 2: MATH_G2, 3: MATH_G3, 4: MATH_G4, 5: MATH_G5}


def _tv_chapters(grade: int) -> List[ChapterDef]:
    themes = [
        ("Em đến trường", "Đọc viết cơ bản"),
        ("Gia đình thân yêu", "Đọc hiểu gia đình"),
        ("Bạn bè và trường học", "Kể chuyện trường lớp"),
        ("Thiên nhiên quanh em", "Văn miêu tả"),
        ("Người thân trong gia đình", "Viết đoạn ngắn"),
        ("Cộng đồng xung quanh", "Đọc hiểu xã hội"),
        ("Ước mơ và hoài bão", "Làm văn"),
        ("Ôn tập học kì 1", "Ôn tập HK1"),
        ("Mùa xuân và lễ hội", "HK2"),
        ("Bảo vệ môi trường", "HK2"),
        ("Ôn tập cuối năm", "Ôn tập HK2"),
    ]
    if grade >= 3:
        themes[4] = ("Văn tả người", "Tập làm văn")
        themes[5] = ("Văn kể chuyện", "Kể chuyện")
    out: List[ChapterDef] = []
    for i, (name, sub) in enumerate(themes):
        ref = f"G{grade}-TV-CD{i+1}"
        lessons = [f"Tuần {i*2+1}: Đọc", f"Tuần {i*2+2}: Viết", "Luyện tập"]
        out.append((f"Chủ đề {i+1}: {name}", sub, ref, lessons))
    return out


def _dao_duc_chapters(grade: int) -> List[ChapterDef]:
    topics = {
        1: ["Em là học sinh lớp Một", "Gọn gàng sạch sẽ", "Chào hỏi lễ phép", "Giúp đỡ bạn bè", "Yêu gia đình", "Ôn tập"],
        2: ["Học tập sinh hoạt đúng giờ", "Biết nói lời yêu thương", "Quan tâm bạn bè", "Giữ lời hứa", "Tiết kiệm", "Ôn tập"],
        3: ["Trung thực trong học tập", "Tôn trọng riêng tư", "Quan tâm hàng xóm", "Tiết kiệm nước điện", "Tôn trọng thư từ", "Ôn tập"],
        4: ["Trung thực tự lực", "Tôn trọng pháp luật", "Yêu lao động", "Bảo vệ môi trường", "Tôn trọng khách", "Ôn tập"],
        5: ["Tự trọng tự tin", "Quyền trẻ em", "Hợp tác cộng đồng", "Kính già yêu trẻ", "Giữ gìn di sản", "Ôn tập"],
    }
    return [
        (f"Bài {i+1}: {t}", f"Đạo đức lớp {grade}", f"G{grade}-DD-{i+1}", ["Khám phá", "Thực hành", "Củng cố"])
        for i, t in enumerate(topics[grade])
    ]


def _tnxh_chapters(grade: int) -> List[ChapterDef]:
    topics = {
        1: ["Cơ thể chúng ta", "Gia đình", "Trường học", "Đường phố an toàn", "Thời tiết", "Ôn tập"],
        2: ["Cơ quan tiêu hóa", "Phòng bệnh", "Gia đình mở rộng", "Trường học", "Cây cối", "Ôn tập"],
        3: ["Hệ vận động", "Hệ tuần hoàn", "Vệ sinh cá nhân", "Làng xóm", "Ngành nghề", "Ôn tập"],
    }
    if grade > 3:
        return []
    return [
        (f"Chủ đề {i+1}: {t}", "TN&XH", f"G{grade}-TNXH-{i+1}", ["Tìm hiểu", "Quan sát", "Luyện tập"])
        for i, t in enumerate(topics[grade])
    ]


def _lsdl_chapters(grade: int) -> List[ChapterDef]:
    topics = {
        4: ["Bản đồ Việt Nam", "Làng quê và thành phố", "Lịch sử địa phương", "Biển đảo", "Bảo vệ thiên nhiên", "Ôn tập"],
        5: ["Dân tộc Việt Nam", "Lịch sử Bắc Bộ", "Lịch sử Nam Bộ", "Địa lý thế giới", "Hợp tác quốc tế", "Ôn tập"],
    }
    return [
        (f"Chủ đề {i+1}: {t}", "Lịch sử & Địa lý", f"G{grade}-LSDL-{i+1}", ["Đọc bản đồ", "Tìm hiểu", "Luyện tập"])
        for i, t in enumerate(topics[grade])
    ]


def _khoa_hoc_chapters(grade: int) -> List[ChapterDef]:
    topics = {
        4: ["Vật chất và năng lượng", "Nhiệt và ánh sáng", "Sinh vật xung quanh", "Môi trường", "An toàn điện", "Ôn tập"],
        5: ["Cơ thể con người", "Vật chất và sự biến đổi", "Thực vật động vật", "Trái đất và mặt trời", "Bảo vệ môi trường", "Ôn tập"],
    }
    return [
        (f"Chủ đề {i+1}: {t}", "Khoa học", f"G{grade}-KH-{i+1}", ["Khám phá", "Thí nghiệm", "Luyện tập"])
        for i, t in enumerate(topics[grade])
    ]


def _generic_chapters(grade: int, slug: str, label: str, count: int = 6) -> List[ChapterDef]:
    return [
        (
            f"Chủ đề {i+1}: {label} — phần {i+1}",
            f"{label} lớp {grade}",
            f"G{grade}-{slug.upper()}-{i+1}",
            [f"Tuần {i*2+1}", f"Tuần {i*2+2}", "Luyện tập"],
        )
        for i in range(count)
    ]


def chapters_for_subject(grade: int, slug: str) -> List[ChapterDef]:
    if slug == "toan":
        return MATH_BY_GRADE[grade]
    if slug == "tieng-viet":
        return _tv_chapters(grade)
    if slug == "dao-duc":
        return _dao_duc_chapters(grade)
    if slug == "tn-xh":
        return _tnxh_chapters(grade)
    if slug == "lich-su-dia-ly":
        return _lsdl_chapters(grade)
    if slug == "khoa-hoc":
        return _khoa_hoc_chapters(grade)
    labels = {
        "the-chat": "Thể chất",
        "nghe-thuat": "Nghệ thuật",
        "hdtn": "Hoạt động trải nghiệm",
        "ngoai-ngu": "Tiếng Anh",
        "tin-hoc": "Tin học",
    }
    return _generic_chapters(grade, slug, labels.get(slug, slug), 6)


def _clear_learning_tables(session: Session) -> None:
    from app.models.learning import (
        LearningChapterProgress,
        LearningDailySummary,
        LearningLessonProgress,
    )

    session.query(LearningLessonProgress).delete(synchronize_session=False)
    session.query(LearningChapterProgress).delete(synchronize_session=False)
    session.query(LearningDailySummary).delete(synchronize_session=False)
    session.query(LearningLesson).delete(synchronize_session=False)
    session.query(LearningChapter).delete(synchronize_session=False)
    session.query(LearningSubject).delete(synchronize_session=False)


def seed_ket_noi_curriculum(session: Session) -> Dict[str, int]:
    """Nạp toàn bộ SGK Kết nối tri thức G1–G5. Trả về thống kê."""
    from app.data.learning_ket_noi_content import begin_global_allocation, end_global_allocation

    _clear_learning_tables(session)
    begin_global_allocation()
    stats = {"subjects": 0, "chapters": 0, "lessons": 0}

    for grade in range(1, 6):
        style = GRADE_STYLE[grade]
        for slug, name, icon, desc, sort_order in SUBJECT_TEMPLATES[grade]:
            sid = f"{slug}-g{grade}"
            session.add(
                LearningSubject(
                    id=sid,
                    grade=grade,
                    name=name,
                    icon=icon,
                    description=desc,
                    is_required=True,
                    sort_order=sort_order,
                    textbook_series=TEXTBOOK,
                    is_active=True,
                    **style,
                )
            )
            stats["subjects"] += 1
    session.flush()

    for grade in range(1, 6):
        for slug, _name, _icon, _desc, _sort in SUBJECT_TEMPLATES[grade]:
            sid = f"{slug}-g{grade}"
            for ci, (ch_name, ch_sub, ref, lesson_titles) in enumerate(chapters_for_subject(grade, slug)):
                ch_id = uuid4()
                ch = LearningChapter(
                    id=ch_id,
                    subject_id=sid,
                    name=ch_name,
                    subtitle=ch_sub,
                    sort_index=ci,
                    est_minutes=min(40, len(lesson_titles) * 8),
                    textbook_ref=ref,
                    is_published=True,
                )
                session.add(ch)
                stats["chapters"] += 1

                ctype = lesson_content_type(slug)
                for li, lt in enumerate(lesson_titles):
                    content = build_lesson_content(grade, slug, ref, ch_name, lt, li)
                    les = LearningLesson(
                        id=uuid4(),
                        chapter_id=ch_id,
                        title=f"Bài {li + 1}: {lt}",
                        summary=f"Micro bài ~5 phút · {ref}",
                        sort_index=li,
                        duration_min=5,
                        content_type=ctype,
                        content_json=content,
                        is_published=True,
                    )
                    session.add(les)
                    stats["lessons"] += 1

    end_global_allocation()
    session.flush()
    return stats


def refresh_all_lesson_content(session: Session) -> int:
    """Cập nhật content_json — mỗi prompt chỉ xuất hiện 1 lần toàn hệ thống."""
    from app.models.learning import LearningChapter, LearningLesson, LearningSubject
    from app.data.learning_ket_noi_content import begin_global_allocation, build_lesson_content, end_global_allocation, lesson_content_type

    begin_global_allocation()
    updated = 0
    lessons = (
        session.query(LearningLesson, LearningChapter, LearningSubject)
        .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
        .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
        .order_by(LearningSubject.grade, LearningSubject.sort_order, LearningChapter.sort_index, LearningLesson.sort_index)
        .all()
    )
    for les, ch, sub in lessons:
        slug = sub.id.rsplit("-g", 1)[0] if "-g" in sub.id else sub.id
        content = build_lesson_content(sub.grade, slug, ch.textbook_ref or "", ch.name, les.title, les.sort_index)
        les.content_json = content
        les.content_type = lesson_content_type(slug)
        updated += 1
    end_global_allocation()
    session.flush()
    return updated


def refresh_subject_lesson_content(session: Session, subject_id: str) -> int:
    """Refresh content_json cho một môn (vd. tieng-viet-g1)."""
    from app.models.learning import LearningChapter, LearningLesson, LearningSubject
    from app.data.learning_ket_noi_content import begin_global_allocation, build_lesson_content, end_global_allocation, lesson_content_type

    begin_global_allocation()
    updated = 0
    lessons = (
        session.query(LearningLesson, LearningChapter, LearningSubject)
        .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
        .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
        .filter(LearningSubject.id == subject_id)
        .order_by(LearningChapter.sort_index, LearningLesson.sort_index)
        .all()
    )
    for les, ch, sub in lessons:
        slug = sub.id.rsplit("-g", 1)[0] if "-g" in sub.id else sub.id
        content = build_lesson_content(sub.grade, slug, ch.textbook_ref or "", ch.name, les.title, les.sort_index)
        les.content_json = content
        les.content_type = lesson_content_type(slug)
        updated += 1
    end_global_allocation()
    session.flush()
    return updated


def delete_ket_noi_curriculum(session: Session) -> None:
    _clear_learning_tables(session)

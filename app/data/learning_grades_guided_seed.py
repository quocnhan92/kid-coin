"""Seed bài guided Giáo viên online — Lớp 2→5 (Tuần 1 mẫu)."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.data.learning_g1_guided_seed import (
    _checkpoint,
    _choice,
    _ensure_guided_lesson,
    _listen_read,
    _listen_read_passage,
    _observe,
    _quiz_step,
    _reward,
    _reindex_steps,
    seed_g1_guided_sample,
)
from app.data.learning_reading_passages import passage_for_guided


def _sid(slug: str, grade: int) -> str:
    return f"{slug}-g{grade}"


def _tv_listen_step(grade: int):
    """Đồng bộ passage Việc nhà — Chủ đề 1 Em đến trường."""
    p = passage_for_guided(grade, "Chủ đề 1: Em đến trường")
    text = p["display_text"]
    words = [w.strip(".,!?;:") for w in text.split() if len(w.strip(".,!?;:")) > 2]
    keywords = list(dict.fromkeys(w.lower() for w in words))[:5]
    return _listen_read(
        text,
        text,
        keywords=keywords,
        emoji="🏫",
        reading_mode="passage" if grade >= 3 else "sentence",
        pass_threshold=75 if grade >= 3 else 80,
        instruction="Con đọc theo thầy từng câu trong bài «Em đến trường» nhé!",
    )


def _week1_specs(grade: int) -> List[Dict[str, Any]]:
    """4 tiết Tuần 1 mẫu theo khung online teacher từng lớp."""
    specs: List[Dict[str, Any]] = [
        {
            "title": f"Tiết 1 — Tiếng Việt (Lớp {grade})",
            "subject_id": _sid("tieng-viet", grade),
            "sort_index": -100,
            "summary": f"Giáo viên online — nhận biết & đọc hiểu Lớp {grade}",
            "progress_emoji": "🍏",
            "steps": _reindex_steps([
                _observe(
                    f"Chào mừng các con đến Lớp {grade}! Cùng ôn và học tiếng Việt nhé!",
                    [{"emoji": "📖", "text": "Đọc to rõ ràng"}, {"emoji": "✏️", "text": "Viết đúng chính tả"}],
                ),
                _tv_listen_step(grade),
                _choice("Bài đọc hôm nay nói về điều gì?", "Chọn đáp án", ["Đi biển", "Đi học", "Đi chợ"], 1),
                _quiz_step([{"prompt": "Đầu câu viết hoa hay thường?", "choices": ["Hoa", "Thường", "Tùy ý"], "answer_index": 0}]),
                _reward("Giỏi lắm! Con đã hoàn thành tiết Tiếng Việt!"),
            ]),
        },
        {
            "title": f"Tiết 2 — Toán (Lớp {grade})",
            "subject_id": _sid("toan", grade),
            "sort_index": -99,
            "summary": f"Giáo viên online — ôn tập toán Lớp {grade}",
            "progress_emoji": "🍋",
            "steps": _reindex_steps([
                _observe(
                    "Cùng nhìn tranh và đếm số lượng trên bảng nhé!",
                    [
                        {"emoji": "🍎", "text": "Ba quả táo"},
                        {"emoji": "➕", "text": "Thêm một quả"},
                        {"emoji": "🔢", "text": "Bốn quả táo"},
                    ],
                ),
                _listen_read(
                    "Trên bàn có ba quả táo. Mẹ thêm một quả nữa. Bây giờ có bốn quả táo.",
                    "Trên bàn có ba quả táo. Mẹ thêm một quả nữa. Bây giờ có bốn quả táo.",
                    keywords=["ba", "một", "bốn", "táo"],
                    emoji="🍎",
                    reading_mode="sentence",
                    instruction="Con đọc câu toán và chú ý các số nhé!",
                ),
                _choice("Ba quả táo thêm một quả bằng mấy quả?", "Chọn đáp án", ["3", "4", "5"], 1),
                _quiz_step([{"prompt": "3 + 1 = ?", "choices": ["3", "4", "5"], "answer_index": 1}]),
                _reward("Xuất sắc! Con làm toán giỏi quá!"),
            ]),
        },
        {
            "title": f"Tiết 3 — Đạo đức (Lớp {grade})",
            "subject_id": _sid("dao-duc", grade),
            "sort_index": -98,
            "summary": f"Giáo viên online — bài đạo đức Lớp {grade}",
            "progress_emoji": "🍇",
            "steps": _reindex_steps([
                _observe(
                    "Bé hãy xem tranh các bạn biết giúp đỡ nhau nhé!",
                    [{"emoji": "🤝", "text": "Giúp bạn"}, {"emoji": "💬", "text": "Nói lời hay"}],
                ),
                _choice("Khi bạn cần giúp, con nên?", "Chọn việc đúng", ["Bỏ đi", "Hỏi thăm và giúp", "Cười"], 1),
                _checkpoint(
                    "Con hãy chia sẻ với bố mẹ một việc tốt con làm hôm nay nhé!",
                    "Bố/Mẹ xác nhận bé đã chia sẻ 👍",
                ),
                _reward("Con là người bạn tốt! 🌟"),
            ]),
        },
    ]

    # Tiết 4 — môn bổ sung theo lớp
    extra_slug = {2: "tn-xh", 3: "tn-xh", 4: "khoa-hoc", 5: "khoa-hoc"}.get(grade, "tn-xh")
    extra_name = {2: "Tự nhiên & Xã hội", 3: "Tự nhiên & Xã hội", 4: "Khoa học", 5: "Khoa học"}.get(grade, "Khám phá")
    specs.append(
        {
            "title": f"Tiết 4 — {extra_name} (Lớp {grade})",
            "subject_id": _sid(extra_slug, grade),
            "sort_index": -97,
            "summary": f"Giáo viên online — khám phá {extra_name} Lớp {grade}",
            "progress_emoji": "🎁",
            "steps": _reindex_steps([
                _observe(
                    f"Cùng tìm hiểu thế giới xung quanh — {extra_name}!",
                    [{"emoji": "🌍", "text": "Quan sát"}, {"emoji": "🔍", "text": "Tìm hiểu"}],
                ),
                _choice("Con học bằng cách nào?", "Chọn cách học tốt", ["Quan sát thực tế", "Đoán bừa", "Bỏ qua"], 0),
                _reward(f"Hoàn thành tiết {extra_name}! 🎉"),
            ]),
        }
    )

    # Tuỳ chỉnh nội dung theo lớp (gợi ý từ learn_struct)
    if grade == 2:
        specs[0]["title"] = "Ôn tập âm vần — Giáo viên online"
        specs[0]["steps"] = _reindex_steps([
            _observe(
                "Chào mừng Lớp 2! Hãy cùng ôn lại các âm vần nhé!",
                [{"emoji": "🌳", "text": "quả chanh"}, {"emoji": "🌸", "text": "hoa trâm"}],
            ),
            _listen_read(
                "Sáng nay, bạn Nam mang quả chanh vàng đến lớp. Các bạn cùng ngửi mùi thơm. Nam chia chanh cho mọi người.",
                "Sáng nay, bạn Nam mang quả chanh vàng đến lớp. Các bạn cùng ngửi mùi thơm. Nam chia chanh cho mọi người.",
                keywords=["nam", "chanh", "lớp", "thơm"],
                emoji="🍋",
                reading_mode="sentence",
            ),
            _choice("Chọn từ đúng", "Từ nào có vần 'anh'?", ["chanh", "cây", "nhà"], 0),
            _choice("Ai mang chanh đến lớp?", "Chọn đáp án", ["Bé Lan", "Bé Nam", "Cô giáo"], 1),
            _reward("Con nhớ bài Lớp 1 giỏi lắm!"),
        ])
        specs[1]["title"] = "Ôn số đến 100 — Giáo viên online"
        specs[1]["steps"] = _reindex_steps([
            _observe(
                "Nhìn bảng số từ 1 đến 100 nhé!",
                [
                    {"emoji": "🔢", "text": "Dãy số 1, 2, 3…"},
                    {"emoji": "➡️", "text": "Số liền sau lớn hơn 1"},
                ],
            ),
            _listen_read(
                "Số liền sau 39 là 40. Số 40 đứng ngay sau 39. Em đếm: ba mươi chín, bốn mươi.",
                "Số liền sau 39 là 40. Số 40 đứng ngay sau 39. Em đếm: ba mươi chín, bốn mươi.",
                keywords=["39", "40", "sau", "đếm"],
                emoji="🔢",
                reading_mode="sentence",
            ),
            _choice("Số liền sau 39 là?", "Chọn đáp án", ["38", "40", "49"], 1),
            _reward("Đếm giỏi quá!"),
        ])
    elif grade == 3:
        specs[0]["title"] = "Đọc hiểu đoạn văn — Giáo viên online"
        specs[0]["steps"] = _reindex_steps([
            _observe(
                "Hôm nay chúng ta đọc đoạn văn về thiên nhiên nhé!",
                [{"emoji": "🌳", "text": "Cây xanh"}, {"emoji": "🐦", "text": "Chim hót"}],
            ),
            _listen_read_passage(
                [
                    {"emoji": "☀️", "text": "Buổi sáng, nắng vàng chiếu qua cửa sổ. Em mang sách ra vườn đọc bài. Gió thổi mát thật dễ chịu."},
                    {"emoji": "🐦", "text": "Chim chích bông hót líu lo trên cành. Em nghe rất vui tai. Em đọc to hơn một chút."},
                ],
                keywords=["sáng", "sách", "chim", "đọc"],
                reading_mode="passage",
                pass_threshold=75,
            ),
            _choice("Em đọc sách ở đâu?", "Chọn đáp án", ["Trong bếp", "Ngoài vườn", "Trong tủ"], 1),
            _reward("Con đọc hiểu giỏi lắm!"),
        ])
        specs[1]["title"] = "Nhân chia cơ bản — Giáo viên online"
        specs[1]["steps"] = _reindex_steps([
            _observe(
                "Cùng xem các nhóm đồ vật trên bảng nhé!",
                [{"emoji": "🍎🍎🍎", "text": "3 quả táo"}, {"emoji": "✖️", "text": "2 nhóm"}, {"emoji": "🔢", "text": "3 × 2 = 6"}],
            ),
            _listen_read(
                "Mỗi nhóm có ba quả táo. Có hai nhóm như vậy. Vậy có sáu quả táo.",
                "Mỗi nhóm có ba quả táo. Có hai nhóm như vậy. Vậy có sáu quả táo.",
                keywords=["ba", "hai", "sáu", "táo"],
                emoji="🍎",
                reading_mode="sentence",
            ),
            _choice("3 × 2 = ?", "Chọn đáp án", ["5", "6", "8"], 1),
            _reward("Con làm toán giỏi!"),
        ])
    elif grade == 4:
        specs[0]["title"] = "Đọc hiểu sâu — Giáo viên online"
        specs[0]["steps"] = _reindex_steps([
            _observe("Hôm nay con đọc đoạn văn kể về ngày đầu tiên đi học.", [{"emoji": "🎒", "text": "Cặp sách mới"}, {"emoji": "🏫", "text": "Trường học"}]),
            _listen_read_passage(
                [
                    {"emoji": "🌅", "text": "Sáng sớm, mẹ đưa em đến trường. Em bỡ ngỡ nhìn bạn mới. Cô giáo mỉm cười chào đón."},
                    {"emoji": "📖", "text": "Tiết đầu tiên, cô dạy em đọc bài. Em đọc to và rõ ràng. Cô khen em chăm ngoan."},
                ],
                reading_mode="passage",
                pass_threshold=72,
            ),
            _choice("Ai đưa em đến trường?", "Chọn đáp án", ["Bố", "Mẹ", "Anh trai"], 1),
            _reward("Con đọc hay và hiểu bài!"),
        ])
        specs[1]["title"] = "Phân số cơ bản — Giáo viên online"
        specs[1]["steps"] = _reindex_steps([
            _observe("Nhìn chiếc bánh được chia đều thành bốn phần.", [{"emoji": "🍰", "text": "1/4 bánh"}, {"emoji": "🍰🍰", "text": "2/4 bánh"}]),
            _listen_read(
                "Chiếc bánh chia làm bốn phần bằng nhau. Lấy một phần ta được một phần tư. Lấy hai phần ta được hai phần tư.",
                "Chiếc bánh chia làm bốn phần bằng nhau. Lấy một phần ta được một phần tư. Lấy hai phần ta được hai phần tư.",
                keywords=["bánh", "bốn", "một", "hai"],
                emoji="🍰",
                reading_mode="passage",
                pass_threshold=72,
            ),
            _choice("2/4 bánh là mấy phần?", "Chọn đáp án", ["1 phần", "2 phần", "4 phần"], 1),
            _reward("Con hiểu phân số giỏi!"),
        ])
    elif grade == 5:
        specs[0]["title"] = "Văn học & viết — Giáo viên online"
        specs[0]["steps"] = _reindex_steps([
            _observe("Đọc đoạn văn tả cảnh làng quê yên bình.", [{"emoji": "🌾", "text": "Cánh đồng"}, {"emoji": "🏡", "text": "Mái nhà tranh"}]),
            _listen_read_passage(
                [
                    {"emoji": "🌅", "text": "Buổi sớm, sương mỏng phủ trên lá. Gà trống gáy vang khắp xóm. Mẹ em ra vườn hái rau."},
                    {"emoji": "🌊", "text": "Con suối nhỏ chảy rì rào bên bờ. Trẻ em reo hò thả diều. Làng quê thật bình yên."},
                    {"emoji": "🌇", "text": "Chiều về, mặt trời lặn sau núi. Khói bếp bay nhẹ trong gió. Em yêu quê hương mình."},
                ],
                reading_mode="passage",
                pass_threshold=70,
            ),
            _choice("Cảnh nào tả buổi chiều?", "Chọn đáp án", ["Đoạn 1", "Đoạn 2", "Đoạn 3"], 2),
            _reward("Con đọc hiểu xuất sắc!"),
        ])
        specs[1]["title"] = "Tỉ lệ & phần trăm — Giáo viên online"
        specs[1]["steps"] = _reindex_steps([
            _observe("Xem bảng tỉ lệ trong lớp học.", [{"emoji": "📊", "text": "10/100 = 10%"}, {"emoji": "💯", "text": "Phần trăm"}]),
            _listen_read(
                "Trong một trăm học sinh, có mười bạn giỏi toán. Mười trên một trăm bằng mười phần trăm. Em ghi: 10%.",
                "Trong một trăm học sinh, có mười bạn giỏi toán. Mười trên một trăm bằng mười phần trăm. Em ghi: 10%.",
                keywords=["mười", "trăm", "phần", "trăm"],
                emoji="📊",
                reading_mode="passage",
                pass_threshold=70,
            ),
            _choice("10/100 = ?", "Chọn đáp án", ["1%", "10%", "100%"], 1),
            _reward("Con làm toán tốt lắm!"),
        ])

    return specs


def seed_grade_guided(session: Session, grade: int) -> Dict[str, Any]:
    if grade == 1:
        return seed_g1_guided_sample(session)
    created: List[str] = []
    for spec in _week1_specs(grade):
        lesson = _ensure_guided_lesson(session, spec)
        if lesson:
            created.append(str(lesson.id))
    session.flush()
    return {"grade": grade, "guided_lessons": created}


def seed_all_guided_lessons(session: Session) -> Dict[str, Any]:
    """Idempotent — seed guided L1–L5."""
    out: Dict[str, Any] = {}
    for g in range(1, 6):
        out[f"grade_{g}"] = seed_grade_guided(session, g)
    return out

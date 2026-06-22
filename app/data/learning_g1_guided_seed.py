"""Seed bài guided G1 Tuần 1 — Giáo viên online (lop1_chitiet_online_teacher)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.learning import (
    LearningChapter,
    LearningGradeSchedule,
    LearningLesson,
    LearningLessonStep,
    LearningScheduleSlot,
    LearningSubject,
)
from app.data.learning_reading_passages import passage_for_guided
from app.data.passages.tv_g1 import BANK as G1_PASSAGE_BANK

GUIDED_LESSON_TITLE = "Âm a — Giáo viên online"

_STANDARD_EMOJIS = ["🍏", "🍋", "🍇", "🎁"]


def _g1_ch1_passage_segments() -> List[Dict[str, str]]:
    segs = G1_PASSAGE_BANK["em đến trường"]["practice_segments"]
    icons = ["🏫", "📚", "🎒"]
    return [{"emoji": icons[i], "text": " ".join(segs[i])} for i in range(len(segs))]


def _g1_ch1_listen_read():
    p = passage_for_guided(1, "Chủ đề 1: Em đến trường")
    text = p["display_text"]
    words = [w.strip(".,!?;:") for w in text.split() if len(w.strip(".,!?;:")) > 2]
    keywords = list(dict.fromkeys(w.lower() for w in words))[:5]
    return _listen_read(
        text,
        text,
        keywords=keywords,
        emoji="🏫",
        reading_mode="sentence",
        instruction="Con đọc ba câu bài «Em đến trường» theo thầy nhé!",
    )


def _listen_read(
    tts: str,
    display_text: str,
    keywords: Optional[List[str]] = None,
    emoji: str = "📖",
    reading_mode: str = "sentence",
    pass_threshold: int = 80,
    max_attempts: int = 5,
    instruction: str = "Con nghe thầy đọc mẫu, rồi đến lượt con đọc to nhé!",
    segments: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    segs = segments or [{"text": display_text, "emoji": emoji}]
    full_text = " ".join(s["text"] for s in segs)
    words = [w for w in full_text.split() if w]
    if keywords is None:
        keywords = [w.lower().strip(".,!?") for w in words[: min(4, len(words))]]
    return {
        "sort_index": 0,
        "step_type": "listen_read",
        "emoji_icon": "👂",
        "est_seconds": 150 if len(segs) > 1 else 120,
        "config_json": {
            "tts_text": tts or full_text,
            "instruction_tts": instruction,
            "display_text": full_text,
            "display_segments": segs,
            "reading_mode": reading_mode,
            "stt_keywords": keywords,
            "pass_threshold": pass_threshold,
            "max_attempts": max_attempts,
            "keyword_mode": reading_mode in ("phoneme", "syllable"),
        },
    }


def _listen_read_passage(
    segments: List[Dict[str, str]],
    instruction: str = "Hôm nay con đọc từng đoạn. Mỗi đoạn con đọc hết rồi mới sang đoạn sau nhé!",
    keywords: Optional[List[str]] = None,
    reading_mode: str = "sentence",
    pass_threshold: int = 80,
) -> Dict[str, Any]:
    full = " ".join(s["text"] for s in segments)
    return _listen_read(
        full,
        full,
        keywords=keywords,
        emoji=segments[0].get("emoji", "📖"),
        reading_mode=reading_mode,
        pass_threshold=pass_threshold,
        instruction=instruction,
        segments=segments,
    )


def _observe(tts: str, blocks: List[Dict[str, str]], auto_sec: int = 8) -> Dict[str, Any]:
    return {
        "sort_index": 0,
        "step_type": "observe",
        "emoji_icon": "👀",
        "est_seconds": 60,
        "config_json": {
            "tts_text": tts,
            "display_blocks": blocks,
            "auto_advance_sec": auto_sec,
        },
    }


def _choice(tts: str, prompt: str, choices: List[str], answer_index: int) -> Dict[str, Any]:
    return {
        "sort_index": 1,
        "step_type": "choice",
        "emoji_icon": "🎯",
        "est_seconds": 45,
        "config_json": {
            "tts_text": tts,
            "prompt": prompt,
            "choices": choices,
            "answer_index": answer_index,
        },
    }


def _quiz_step(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "sort_index": 2,
        "step_type": "quiz",
        "emoji_icon": "📝",
        "est_seconds": 90,
        "config_json": {"questions": questions, "pass_score": 100},
    }


def _checkpoint(tts: str, label: str = "Bố/Mẹ xác nhận bé đã làm 👍") -> Dict[str, Any]:
    return {
        "sort_index": 3,
        "step_type": "family_checkpoint",
        "emoji_icon": "👨‍👩‍👦",
        "est_seconds": 120,
        "config_json": {
            "tts_text": tts,
            "parent_button_label": label,
            "notify_parent": True,
        },
    }


def _reward(tts: str) -> Dict[str, Any]:
    return {
        "sort_index": 4,
        "step_type": "reward",
        "emoji_icon": "🎁",
        "est_seconds": 15,
        "is_required": False,
        "config_json": {
            "tts_text": tts,
            "emoji_burst": ["🎉", "⭐", "🥳"],
        },
    }


def _reindex_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for i, s in enumerate(steps):
        row = dict(s)
        row["sort_index"] = i
        out.append(row)
    return out


G1_WEEK1_GUIDED: List[Dict[str, Any]] = [
    {
        "title": GUIDED_LESSON_TITLE,
        "subject_id": "tieng-viet-g1",
        "sort_index": -100,
        "summary": "Tiết 30 phút — nhận biết âm a, tương tác với bố mẹ",
        "progress_emoji": "🍏",
        "steps": _reindex_steps([
            _observe(
                "Bé ơi, nhìn các từ có âm A và đọc theo thầy nhé!",
                [{"emoji": "🌳", "text": "Nhà a"}, {"emoji": "🪵", "text": "Má a"}, {"emoji": "🌿", "text": "Lá a"}],
            ),
            _listen_read(
                "Ba đi chợ mua cá. Mẹ ở nhà nấu cơm. Bé Lan ngồi xem tranh.",
                "Ba đi chợ mua cá. Mẹ ở nhà nấu cơm. Bé Lan ngồi xem tranh.",
                keywords=["ba", "mẹ", "lan", "cá"],
                emoji="🏠",
                reading_mode="sentence",
                instruction="Bài đầu tiên: con đọc ba câu ngắn theo thầy nhé!",
            ),
            _choice("Con hãy chọn chữ có âm A!", "Chữ nào có âm A?", ["a", "b", "c"], 0),
            _quiz_step([{"prompt": "Trong bài đọc, ai ngồi xem tranh?", "choices": ["Bé Lan", "Bé Nam", "Cô giáo"], "answer_index": 0}]),
            _checkpoint("Con hãy quay sang chào bố hoặc mẹ thật lễ phép nào!", "Bố/Mẹ xác nhận bé đã chào 👍"),
            _reward("Xuất sắc quá! Con được thưởng một ngôi sao!"),
        ]),
    },
    {
        "title": "Âm b — Ghép ba",
        "subject_id": "tieng-viet-g1",
        "sort_index": -99,
        "summary": "Nhận biết âm b, ghép tiếng ba — Giáo viên online",
        "progress_emoji": "🍋",
        "steps": _reindex_steps([
            _observe(
                "Tìm các vật bắt đầu bằng âm B nhé!",
                [{"emoji": "🪟", "text": "Bàn"}, {"emoji": "⚽", "text": "Bóng"}, {"emoji": "🧸", "text": "Búp bê"}],
            ),
            _listen_read(
                "Bé Nam mang bóng đến sân. Các bạn cùng chơi rất vui. Bóng lăn nhanh trên cỏ xanh. Nam cười thật tươi.",
                "Bé Nam mang bóng đến sân. Các bạn cùng chơi rất vui. Bóng lăn nhanh trên cỏ xanh. Nam cười thật tươi.",
                keywords=["nam", "bóng", "sân", "vui"],
                emoji="⚽",
                reading_mode="sentence",
            ),
            _choice("Con chọn tiếng ghép đúng nhé: bờ - a - ?", "Tiếng nào là ba?", ["ab", "ba", "ca"], 1),
            _choice("Ai mang bóng đến sân?", "Chọn đáp án", ["Bé Lan", "Bé Nam", "Bé An"], 1),
            _reward("Giỏi lắm! Con đã học xong âm b!"),
        ]),
    },
    {
        "title": "Em đến trường — Đọc theo thầy",
        "subject_id": "tieng-viet-g1",
        "sort_index": -97,
        "summary": "Đọc đoạn Chủ đề 1 — đồng bộ Việc nhà G1",
        "progress_emoji": "🏫",
        "steps": _reindex_steps([
            _observe(
                "Hôm nay con đọc bài «Em đến trường» giống bài Việc nhà nhé!",
                [{"emoji": "🏫", "text": "Đến trường"}, {"emoji": "🎒", "text": "Cặp sách"}, {"emoji": "👩‍🏫", "text": "Cô giáo"}],
            ),
            _g1_ch1_listen_read(),
            _quiz_step([
                {"prompt": "Trong bài, ai dắt tay bé đi học?", "choices": ["Mẹ", "Bác sĩ", "Cô lao công"], "answer_index": 0},
                {"prompt": "Bé mang gì đến trường?", "choices": ["Cặp mới", "Xe đạp lớn", "Tivi"], "answer_index": 0},
            ]),
            _reward("Con đọc hay! Bài Em đến trường giỏi lắm! 🌟"),
        ]),
    },
    {
        "title": "Luyện đọc — Giáo viên online",
        "subject_id": "tieng-viet-g1",
        "sort_index": -98,
        "summary": "Đọc ba đoạn ngắn — mỗi đoạn ba câu",
        "progress_emoji": "🍊",
        "steps": _reindex_steps([
            _observe(
                "Hôm nay con đọc ba đoạn ngắn. Mỗi đoạn ba câu nhé!",
                [
                    {"emoji": "👨‍👩‍👧", "text": "Đoạn 1: Gia đình"},
                    {"emoji": "🏫", "text": "Đoạn 2: Trường lớp"},
                    {"emoji": "🌳", "text": "Đoạn 3: Cây xanh"},
                ],
            ),
            _listen_read_passage(
                _g1_ch1_passage_segments(),
                keywords=["trường", "bé", "cô", "học"],
            ),
            _choice("Đoạn nào nói về trường lớp?", "Chọn đáp án", ["Đoạn 1", "Đoạn 2", "Đoạn 3"], 1),
            _reward("Con đọc hay quá! Ba đoạn đều giỏi! 🌟"),
        ]),
    },
    {
        "title": "Số 1, 2, 3 — Giáo viên online",
        "subject_id": "toan-g1",
        "sort_index": -100,
        "summary": "Đếm và nhận biết số 1, 2, 3",
        "progress_emoji": "🍇",
        "steps": _reindex_steps([
            _observe(
                "Cùng đếm trong tranh: một mặt trời, hai đám mây, ba chú chim!",
                [
                    {"emoji": "☀️", "text": "Một mặt trời"},
                    {"emoji": "☁️", "text": "Hai đám mây"},
                    {"emoji": "🐦", "text": "Ba chú chim"},
                ],
            ),
            _listen_read(
                "Trên trời có một mặt trời. Trên trời có hai đám mây. Dưới cây có ba chú chim.",
                "Trên trời có một mặt trời. Trên trời có hai đám mây. Dưới cây có ba chú chim.",
                keywords=["một", "hai", "ba", "chim"],
                emoji="🔢",
                reading_mode="sentence",
                instruction="Con đọc theo thầy và đếm số lượng nhé!",
            ),
            _choice("Có bao nhiêu chú chim trong tranh?", "Chọn số đúng", ["1", "2", "3"], 2),
            _quiz_step([{"prompt": "Trên trời có mấy đám mây?", "choices": ["1", "2", "3"], "answer_index": 1}]),
            _reward("Con đếm giỏi quá! ⭐"),
        ]),
    },
    {
        "title": "Em biết lễ phép — Giáo viên online",
        "subject_id": "dao-duc-g1",
        "sort_index": -100,
        "summary": "Học cách chào hỏi lễ phép cùng bố mẹ",
        "progress_emoji": "🎁",
        "steps": _reindex_steps([
            _observe(
                "Bé hãy xem bạn nhỏ khoanh tay chào ông bà khi đi học về nhé!",
                [{"emoji": "👴", "text": "Con chào ông bà ạ!"}],
            ),
            _choice("Khi gặp người lớn, con nên?", "Chọn cách đúng", ["Quay lưng đi", "Khoanh tay chào", "Chạy đi chơi"], 1),
            _checkpoint(
                "Con hãy quay sang khoanh tay, cúi đầu nhẹ và chào bố hoặc mẹ thật lễ phép nào!",
                "Bố/Mẹ xác nhận bé đã chào lễ phép 👍",
            ),
            _reward("Con là học sinh ngoan! 🌟"),
        ]),
    },
]


def _first_chapter(session: Session, subject_id: str) -> Optional[LearningChapter]:
    return (
        session.query(LearningChapter)
        .filter(LearningChapter.subject_id == subject_id, LearningChapter.is_published.is_(True))
        .order_by(LearningChapter.sort_index)
        .first()
    )


def _sync_steps(session: Session, lesson: LearningLesson, steps: List[Dict[str, Any]]) -> None:
    existing = (
        session.query(LearningLessonStep)
        .filter(LearningLessonStep.lesson_id == lesson.id)
        .order_by(LearningLessonStep.sort_index)
        .all()
    )
    specs = sorted(steps, key=lambda s: s["sort_index"])

    def _add(spec: Dict[str, Any]) -> None:
        session.add(
            LearningLessonStep(
                id=uuid.uuid4(),
                lesson_id=lesson.id,
                sort_index=spec["sort_index"],
                step_type=spec["step_type"],
                emoji_icon=spec["emoji_icon"],
                config_json=spec["config_json"],
                est_seconds=spec["est_seconds"],
                is_required=spec.get("is_required", True),
            )
        )

    if not existing:
        for spec in specs:
            _add(spec)
        session.flush()
        return

    if len(existing) == len(specs):
        for row, spec in zip(existing, specs):
            row.step_type = spec["step_type"]
            row.emoji_icon = spec["emoji_icon"]
            row.config_json = spec["config_json"]
            row.est_seconds = spec["est_seconds"]
            row.is_required = spec.get("is_required", True)
        session.flush()
        return

    for row in existing:
        session.delete(row)
    session.flush()
    for spec in specs:
        _add(spec)
    session.flush()


def _ensure_steps(session: Session, lesson: LearningLesson, steps: List[Dict[str, Any]]) -> None:
    _sync_steps(session, lesson, steps)


def _ensure_guided_lesson(session: Session, spec: Dict[str, Any]) -> Optional[LearningLesson]:
    subject = session.query(LearningSubject).filter(LearningSubject.id == spec["subject_id"]).first()
    if not subject:
        return None
    chapter = _first_chapter(session, spec["subject_id"])
    if not chapter:
        return None

    lesson = (
        session.query(LearningLesson)
        .filter(LearningLesson.chapter_id == chapter.id, LearningLesson.title == spec["title"])
        .first()
    )
    if not lesson:
        lesson = LearningLesson(
            id=uuid.uuid4(),
            chapter_id=chapter.id,
            title=spec["title"],
            summary=spec["summary"],
            sort_index=spec["sort_index"],
            duration_min=30,
            content_type="guided",
            content_json={},
            progress_emoji=spec.get("progress_emoji", "🍏"),
            is_published=True,
        )
        session.add(lesson)
        session.flush()
    else:
        lesson.content_type = "guided"
        lesson.summary = spec["summary"]
        lesson.sort_index = spec["sort_index"]
        lesson.progress_emoji = spec.get("progress_emoji", lesson.progress_emoji)
        session.flush()

    _ensure_steps(session, lesson, spec["steps"])
    return lesson


def seed_g1_guided_sample(session: Session) -> Dict[str, Any]:
    """Idempotent — thêm bài guided Tuần 1 G1 + lịch tuần 1."""
    created: List[str] = []
    first_lesson: Optional[LearningLesson] = None
    for spec in G1_WEEK1_GUIDED:
        lesson = _ensure_guided_lesson(session, spec)
        if lesson:
            created.append(str(lesson.id))
            if first_lesson is None:
                first_lesson = lesson

    if not first_lesson:
        return {"guided_lessons": [], "schedule": None}

    schedule = (
        session.query(LearningGradeSchedule)
        .filter(LearningGradeSchedule.grade == 1, LearningGradeSchedule.label == "Tuần 1")
        .first()
    )
    if not schedule:
        schedule = LearningGradeSchedule(
            id=uuid.uuid4(),
            grade=1,
            semester=1,
            week_number=1,
            label="Tuần 1",
            is_active=True,
        )
        session.add(schedule)
        session.flush()

        tv = _ensure_guided_lesson(session, G1_WEEK1_GUIDED[0])
        tv_b = _ensure_guided_lesson(session, G1_WEEK1_GUIDED[1])
        toan = _ensure_guided_lesson(session, G1_WEEK1_GUIDED[2])
        dao = _ensure_guided_lesson(session, G1_WEEK1_GUIDED[3])

        slots_spec = [
            (1, "morning", 1, "tieng-viet-g1", tv.id if tv else None),
            (1, "morning", 2, "tieng-viet-g1", tv_b.id if tv_b else None),
            (1, "afternoon", 1, "toan-g1", toan.id if toan else None),
            (1, "afternoon", 2, "dao-duc-g1", dao.id if dao else None),
        ]
        for weekday, session_name, slot_order, subject_id, lesson_id in slots_spec:
            if lesson_id is None:
                subj = session.query(LearningSubject).filter(LearningSubject.id == subject_id).first()
                if subj:
                    ch = _first_chapter(session, subject_id)
                    if ch:
                        les = (
                            session.query(LearningLesson)
                            .filter(
                                LearningLesson.chapter_id == ch.id,
                                LearningLesson.is_published.is_(True),
                                LearningLesson.content_type == "guided",
                            )
                            .order_by(LearningLesson.sort_index)
                            .first()
                        )
                        lesson_id = les.id if les else None
            session.add(
                LearningScheduleSlot(
                    id=uuid.uuid4(),
                    schedule_id=schedule.id,
                    weekday=weekday,
                    session=session_name,
                    slot_order=slot_order,
                    subject_id=subject_id,
                    lesson_id=lesson_id,
                )
            )

    session.flush()
    return {"guided_lessons": created, "schedule": str(schedule.id)}


def ensure_g1_guided_for_tests(session: Session) -> LearningLesson:
    """Gọi từ test fixture khi migration chưa chạy."""
    seed_g1_guided_sample(session)
    session.flush()
    lesson = (
        session.query(LearningLesson)
        .filter(LearningLesson.title == GUIDED_LESSON_TITLE, LearningLesson.content_type == "guided")
        .first()
    )
    if not lesson:
        raise RuntimeError("Cannot seed guided lesson — tieng-viet-g1 missing")
    return lesson

"""Đoạn văn đọc hiểu — chọn bank theo lớp, nội dung gốc."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.data.passages import tv_g1, tv_g2

# G3–G5: dùng bank chung tạm (Phase 3 sẽ tách riêng)
_LEGACY_BANK: Dict[str, Dict[str, Any]] = {
    "em đến trường": {
        "read_short": [
            "Sáng sớm, mẹ dắt tay em đến trường.",
            "Em mang cặp mới, bước vào lớp thật hồi hộp.",
            "Cô giáo mỉm cười chào đón em và các bạn.",
        ],
        "read_mid": [
            "Hôm nay là ngày đầu tiên em đi học.",
            "Trên đường, em gặp bạn Nam cũng đang đến trường.",
            "Hai bạn cùng nhau bước qua cổng trường rộng.",
            "Tiếng trống khai giảng vang lên thật vui tai.",
        ],
        "practice_segments": [
            ["Buổi sáng, lớp em học bài đọc mới.", "Cô giáo đọc mẫu, em đọc theo thật to.", "Các bạn vỗ tay khen em đọc hay."],
            ["Em thích đến trường mỗi ngày.", "Trường học là nơi em học và chơi.", "Em kết bạn với nhiều bạn mới."],
            ["Chiều về em kể cho mẹ nghe.", "Mẹ mỉm cười lắng nghe.", "Em mong ngày mai đến trường."],
        ],
    },
}

_GRADE_BANKS = {1: tv_g1.BANK, 2: tv_g2.BANK}
_VERSIONS = {1: tv_g1.CONTENT_VERSION, 2: tv_g2.CONTENT_VERSION}


def content_version_for_grade(grade: int) -> str:
    return _VERSIONS.get(grade, "tv-shared-v0")


def _topic_key(chapter: str) -> str:
    topic = chapter.split(":")[-1].strip() if ":" in chapter else chapter
    return topic.lower()


def _chapter_num(chapter: str) -> int:
    m = re.match(r"Chủ đề\s+(\d+)", chapter)
    return int(m.group(1)) if m else 1


def _bank_for_grade(grade: int, topic_key: str) -> Dict[str, Any]:
    grade_bank = _GRADE_BANKS.get(grade, {})
    if topic_key in grade_bank:
        return grade_bank[topic_key]
    if topic_key in _LEGACY_BANK:
        return _LEGACY_BANK[topic_key]
    return _generic_topic(topic_key)


def _generic_topic(topic_key: str) -> Dict[str, Any]:
    return {
        "read_short": [
            f"Chủ đề hôm nay là {topic_key}.",
            "Em đọc thật chăm từng câu trong đoạn văn.",
            "Em ghi nhớ từ mới để trả lời câu hỏi.",
        ],
        "read_mid": [
            f"Buổi học về {topic_key} thật bổ ích.",
            "Em đọc to và rõ từng câu.",
            "Cô giáo hướng dẫn em đọc đúng dấu câu.",
            "Em cảm thấy tự tin hơn khi đọc trước lớp.",
        ],
        "practice_segments": [
            [f"Cuối bài, em ôn lại đoạn văn về {topic_key}.", "Em đọc lại một lần nữa thật chậm.", "Em trả lời câu hỏi dựa trên nội dung."],
            ["Em chia sẻ điều em thích trong bài.", "Em học thêm từ mới.", "Em viết lại một câu yêu thích."],
            ["Em tự hào vì đã đọc hết bài.", "Em sẵn sàng làm bài tập.", "Em cảm ơn cô giáo."],
        ],
    }


def _flatten_segments(segments: List[List[str]]) -> List[str]:
    out: List[str] = []
    for seg in segments:
        out.extend(seg)
    return out


def build_reading_passage(
    chapter: str,
    lesson_title: str,
    idx: int,
    grade: int = 1,
) -> Dict[str, Any]:
    """Đọc: 3 câu (chủ đề 1) hoặc 4–5 câu; Viết: mẫu ngắn; Luyện tập: 3×3 câu."""
    topic = chapter.split(":")[-1].strip() if ":" in chapter else chapter
    key = _topic_key(chapter)
    bank = _bank_for_grade(grade, key)
    ch_num = _chapter_num(chapter)
    segments: Optional[List[List[str]]] = None

    if "Luyện tập" in lesson_title or idx >= 2:
        segments = [list(s) for s in bank["practice_segments"]]
        sentences = _flatten_segments(segments)
    elif "Viết" in lesson_title or idx == 1:
        sentences = list(bank["read_short"][:3])
    else:
        if ch_num == 1:
            sentences = list(bank["read_short"][:3])
        else:
            sentences = list(bank["read_mid"])

    return {
        "passage_title": topic,
        "passage": sentences,
        "passage_segments": segments,
        "content_version": content_version_for_grade(grade),
    }


def passage_for_guided(grade: int, chapter_name: str, *, practice: bool = False) -> Dict[str, Any]:
    """Lấy đoạn văn cho Giáo viên online — cùng bank Việc nhà."""
    key = _topic_key(chapter_name)
    bank = _bank_for_grade(grade, key)
    if practice:
        segs = bank["practice_segments"]
        return {
            "segments": [{"emoji": "📖", "text": " ".join(seg)} for seg in segs],
            "display_text": " ".join(_flatten_segments(segs)),
            "keywords": [],
        }
    short = bank["read_short"]
    text = " ".join(short)
    return {"display_text": text, "keywords": [], "segments": None}

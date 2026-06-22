"""Phân bổ câu hỏi toàn cục — mỗi prompt chỉ xuất hiện 1 lần."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.data.learning_ket_noi_questions_bank import BANK, get_bank_questions

Question = Dict[str, Any]


def _norm(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt.strip().lower())


def _q(prompt: str, choices: List[str], answer_index: int = 0) -> Question:
    return {"prompt": prompt, "choices": choices, "answer_index": answer_index}


class GlobalQuestionAllocator:
    """Đảm bảo không trùng prompt trong toàn bộ G1–G5."""

    def __init__(self) -> None:
        self.used: Set[str] = set()

    def is_used(self, prompt: str) -> bool:
        return _norm(prompt) in self.used

    def claim(self, q: Question) -> Optional[Question]:
        key = _norm(q["prompt"])
        if key in self.used:
            return None
        self.used.add(key)
        return q

    def claim_many(self, candidates: List[Question], count: int = 3) -> List[Question]:
        out: List[Question] = []
        for q in candidates:
            claimed = self.claim(q)
            if claimed:
                out.append(claimed)
            if len(out) >= count:
                break
        return out


def _serial_hash(serial: int, salt: str) -> int:
    h = hashlib.md5(f"{serial}:{salt}".encode()).hexdigest()
    return int(h[:8], 16)


def _is_practice(lesson_title: str, lesson_idx: int) -> bool:
    t = lesson_title.lower()
    return lesson_idx >= 2 or "luyện" in t or "ôn tập" in t or "kiểm tra" in t


def _math_candidates(serial: int, grade: int, ref: str, practice: bool) -> List[Question]:
    offset = 1000 if practice else 0
    s = serial + offset
    out: List[Question] = []
    for i in range(12):
        h = _serial_hash(s, f"m{i}")
        a = (h % (40 + grade * 10)) + grade + 1 + i
        b = (h // 7 % 9) + 1
        c = a + b
        d = max(a, b) - min(a, b)
        templates = [
            _q(f"Tính: {a} + {b} = ?", [str(c), str(c + 1), str(max(0, c - 1))], 0),
            _q(f"Tính: {max(a,b)} − {min(a,b)} = ?", [str(d), str(d + 1), str(max(0, d - 1))], 0),
            _q(f"Số liền sau của {a} là?", [str(a + 1), str(a), str(a + 2)], 0),
            _q(f"Số liền trước của {a + b} là?", [str(a + b - 1), str(a + b), str(a + b + 1)], 0),
            _q(f"So sánh: {a} và {b} — số nào lớn hơn?", [str(max(a, b)), str(min(a, b)), "Bằng nhau"], 0),
        ]
        if practice:
            templates.append(
                _q(f"Luyện tập: {a} + {b} + 1 = ?", [str(c + 1), str(c), str(c + 2)], 0)
            )
        out.append(templates[i % len(templates)])
    return out


def _topic_from_chapter(chapter: str) -> str:
    if ":" in chapter:
        return chapter.split(":", 1)[1].strip()
    return chapter.strip()


def _knowledge_candidates(
    serial: int,
    grade: int,
    subject_slug: str,
    textbook_ref: str,
    chapter: str,
    lesson_title: str,
    practice: bool,
) -> List[Question]:
    topic = _topic_from_chapter(chapter)
    bank = get_bank_questions(textbook_ref)
    out: List[Question] = list(bank)

    traits = [
        "biết chia sẻ", "giữ lời hợp", "tôn trọng người khác", "yêu thiên nhiên",
        "học tập chăm chỉ", "ăn uống lành mạnh", "vận động an toàn", "tiết kiệm",
    ]
    h = _serial_hash(serial, "k")
    trait = traits[h % len(traits)]
    tag = f"B{serial}"

    base = [
        _q(
            f"({tag}) «{topic}» L{grade}: điều nào đúng?",
            [f"Liên quan kiến thức {topic}", "Không liên quan", "Chỉ là trò chơi"],
            0,
        ),
        _q(
            f"({tag}) Với «{topic}», bé nên {trait} vì sao?",
            ["Giúp học tốt hơn", "Để bỏ học", "Không cần thiết"],
            0,
        ),
        _q(
            f"({tag}) Học «{lesson_title}»: bé làm gì phù hợp?",
            ["Đọc SGK và hỏi bố mẹ", "Đoán đáp án", "Bỏ qua bài"],
            0,
        ),
        _q(
            f"({tag}) «{topic}» — ví dụ đúng trong SGK?",
            [f"Nội dung thuộc {topic}", "Nội dung không liên quan", "Truyện tranh"],
            0,
        ),
    ]
    if practice:
        base.extend([
            _q(
                f"({tag}) Luyện «{topic}»: khái niệm quan trọng là?",
                [f"Nắm vững {topic}", "Không cần nhớ", "Chỉ cần chơi"],
                0,
            ),
            _q(
                f"({tag}) Ôn «{lesson_title}»: em chọn phương án đúng?",
                ["Áp dụng kiến thức đã học", "Chọn ngẫu nhiên", "Bỏ trống"],
                0,
            ),
        ])
    if subject_slug == "tieng-viet":
        base.extend([
            _q(f"({tag}) «{topic}»: từ chỉ sự vật là?", ["Danh từ", "Động từ", "Tính từ"], 0),
            _q(f"({tag}) Đọc «{lesson_title}»: dấu chấm dùng khi nào?", ["Hết câu", "Giữa câu", "Đầu đoạn"], 0),
            _q(f"({tag}) «{topic}» thuộc thể loại?", ["Văn bản học tập", "Toán", "Thể thao"], 0),
        ])

    for i in range(12):
        hh = _serial_hash(serial + i, subject_slug)
        t = traits[hh % len(traits)]
        out.append(
            _q(
                f"({tag}-{i}) «{topic}» — {t} liên quan thế nào?",
                [f"Gắn với bài {lesson_title}", "Không liên quan", "Chỉ để chơi"],
                0,
            )
        )
    out.extend(base)
    return out


def allocate_lesson_questions(
    allocator: GlobalQuestionAllocator,
    *,
    lesson_serial: int,
    grade: int,
    subject_slug: str,
    textbook_ref: str,
    chapter: str,
    lesson_title: str,
    lesson_idx: int,
    count: int = 3,
) -> List[Question]:
    practice = _is_practice(lesson_title, lesson_idx)
    if subject_slug == "toan":
        pool = _math_candidates(lesson_serial, grade, textbook_ref, practice)
    else:
        pool = _knowledge_candidates(
            lesson_serial, grade, subject_slug, textbook_ref, chapter, lesson_title, practice
        )

    picked = allocator.claim_many(pool, count)

    # Sinh thêm cho đến khi đủ 3 câu unique
    attempt = 0
    while len(picked) < count and attempt < 30:
        extra_serial = lesson_serial * 100 + attempt
        extra_pool = (
            _math_candidates(extra_serial, grade, textbook_ref, practice)
            if subject_slug == "toan"
            else _knowledge_candidates(
                extra_serial, grade, subject_slug, textbook_ref, chapter, lesson_title, practice
            )
        )
        for q in extra_pool:
            c = allocator.claim(q)
            if c:
                picked.append(c)
            if len(picked) >= count:
                break
        attempt += 1

    return picked[:count]


def audit_duplicates(lessons_content: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    from collections import Counter

    prompts: List[str] = []
    for cj in lessons_content:
        for q in cj.get("questions", []):
            prompts.append(q.get("prompt", ""))
    cnt = Counter(p for p in prompts if p)
    return [(p, n) for p, n in cnt.items() if n > 1]

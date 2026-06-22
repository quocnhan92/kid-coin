"""Câu hỏi đọc hiểu sinh từ passage — thay template meta TV."""

from __future__ import annotations

import hashlib
from typing import List

from app.data.learning_question_allocator import GlobalQuestionAllocator, Question, _q

_WHO_PATTERNS = [
    "cô giáo",
    "bé lan",
    "bé nam",
    "bé hoa",
    "bạn hoa",
    "bạn nam",
    "bạn mai",
    "bạn hùng",
    "ông bà",
    "bà",
    "ông",
    "mẹ",
    "ba",
    "minh",
    "linh",
    "bé",
    "bạn",
    "cô",
    "thầy",
]

_WRONG_WHO = [
    "Bác sĩ",
    "Cô lao công",
    "Bác tài xế",
    "Chú công an",
    "Bạn Tuấn",
    "Cô y tá",
    "Ông hàng xóm",
]

_WRONG_ACTIONS = [
    "Đi ngủ cả ngày",
    "Chơi game suốt đêm",
    "Không đến trường",
    "Xem tivi không học",
    "Vứt rác bừa bãi",
    "Không chào hỏi",
]

_WRONG_TOPICS = [
    "Chơi game",
    "Làm toán nâng cao",
    "Thể dục nhảy dây",
    "Nấu ăn trong nhà hàng",
]


def _short(text: str, max_len: int = 48) -> str:
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _find_who(sentence: str) -> str:
    low = sentence.lower()
    for pat in _WHO_PATTERNS:
        if pat in low:
            if pat == "bé lan":
                return "Bé Lan"
            if pat == "bé nam":
                return "Bé Nam"
            if pat == "bé hoa":
                return "Bé Hoa"
            if pat == "bạn hoa":
                return "Bạn Hoa"
            if pat == "bạn nam":
                return "Bạn Nam"
            if pat == "bạn mai":
                return "Bạn Mai"
            if pat == "bạn hùng":
                return "Bạn Hùng"
            if pat == "cô giáo":
                return "Cô giáo"
            if pat == "ông bà":
                return "Ông bà"
            if pat in ("minh", "linh"):
                return pat.capitalize()
            if pat == "mẹ":
                return "Mẹ"
            if pat == "ba":
                return "Ba"
            if pat == "bé":
                return "Bé"
            if pat == "bạn":
                return "Bạn bè"
            if pat == "cô":
                return "Cô giáo"
            return pat.capitalize()
    return "Nhân vật trong bài"


def _mutate_sentence(sentence: str, salt: int) -> str:
    """Câu sai — không có trong passage (để làm đáp án nhiễu)."""
    variants = [
        sentence.replace("đến trường", "đi siêu thị"),
        sentence.replace("mẹ", "bác sĩ"),
        sentence.replace("bé", "chú chó"),
        sentence.replace("cô giáo", "bác tài xế"),
        sentence.replace("học", "ngủ"),
        sentence.replace("đọc", "vẽ"),
        "Trời mưa to, không ai ra ngoài.",
        "Bé ở nhà xem phim hoạt hình.",
    ]
    return variants[salt % len(variants)]


def _pick_distractors(correct: str, pool: List[str], count: int, seed: int) -> List[str]:
    out: List[str] = []
    i = 0
    while len(out) < count and i < len(pool) * 3:
        cand = pool[(seed + i) % len(pool)]
        if cand != correct and cand not in out:
            out.append(cand)
        i += 1
    while len(out) < count:
        out.append(f"Đáp án khác {len(out)}")
    return out


def build_passage_question_candidates(
    *,
    passage: List[str],
    passage_title: str,
    textbook_ref: str,
    lesson_title: str,
    lesson_serial: int,
    grade: int,
) -> List[Question]:
    if not passage:
        return []

    tag = f"{textbook_ref}-S{lesson_serial}"
    candidates: List[Question] = []
    s0, s_mid, s_last = passage[0], passage[len(passage) // 2], passage[-1]

    who0 = _find_who(s0)
    w_wrong = _pick_distractors(who0, _WRONG_WHO, 2, lesson_serial)
    candidates.append(
        _q(
            f"({tag}) Câu đầu bài «{passage_title}»: ai được nhắc đến?",
            [who0, w_wrong[0], w_wrong[1]],
            0,
        )
    )

    wrong_s1 = _mutate_sentence(s_mid, lesson_serial)
    wrong_s2 = _mutate_sentence(s_last, lesson_serial + 1)
    opts = [s_mid, wrong_s1, wrong_s2]
    # xáo nhưng giữ đáp án đúng ở index 0
    candidates.append(
        _q(
            f"({tag}) Câu nào đúng với nội dung đoạn «{passage_title}»?",
            opts,
            0,
        )
    )

    topic_wrong = _pick_distractors(passage_title, _WRONG_TOPICS, 2, lesson_serial + 2)
    candidates.append(
        _q(
            f"({tag}) Đoạn văn «{passage_title}» chủ yếu nói về?",
            [passage_title, topic_wrong[0], topic_wrong[1]],
            0,
        )
    )

    for i, sent in enumerate(passage):
        who = _find_who(sent)
        ww = _pick_distractors(who, _WRONG_WHO, 2, lesson_serial + i + 10)
        candidates.append(
            _q(
                f"({tag}-c{i}) Trong câu «{_short(sent)}», nhân vật là?",
                [who, ww[0], ww[1]],
                0,
            )
        )
        act_wrong = _pick_distractors(sent, _WRONG_ACTIONS, 2, lesson_serial + i + 20)
        candidates.append(
            _q(
                f"({tag}-c{i}) Câu «{_short(sent)}» kể về việc gì?",
                [sent, act_wrong[0], act_wrong[1]],
                0,
            )
        )

    if "Viết" in lesson_title:
        candidates.append(
            _q(
                f"({tag}) Bài Viết «{passage_title}»: em tập viết theo mẫu nào?",
                [f"Đoạn mẫu {_short(s0)}", "Truyện tranh", "Bài hát"],
                0,
            )
        )
    if "Luyện" in lesson_title:
        candidates.append(
            _q(
                f"({tag}) Luyện tập «{passage_title}»: đoạn văn có mấy ý chính?",
                [str(max(1, len(passage) // 3)), "1 ý", "10 ý"],
                0,
            )
        )

    return candidates


def allocate_passage_reading_questions(
    allocator: GlobalQuestionAllocator,
    *,
    passage: List[str],
    passage_title: str,
    textbook_ref: str,
    lesson_title: str,
    lesson_serial: int,
    grade: int,
    count: int = 3,
) -> List[Question]:
    pool = build_passage_question_candidates(
        passage=passage,
        passage_title=passage_title,
        textbook_ref=textbook_ref,
        lesson_title=lesson_title,
        lesson_serial=lesson_serial,
        grade=grade,
    )
    # ổn định thứ tự nhưng khác pool theo serial
    h = int(hashlib.md5(f"{lesson_serial}:{textbook_ref}".encode()).hexdigest()[:8], 16)
    rotated = pool[h % max(1, len(pool)) :] + pool[: h % max(1, len(pool))]
    picked = allocator.claim_many(rotated, count)

    attempt = 0
    while len(picked) < count and attempt < 20:
        extra = build_passage_question_candidates(
            passage=passage,
            passage_title=passage_title,
            textbook_ref=f"{textbook_ref}-x{attempt}",
            lesson_title=lesson_title,
            lesson_serial=lesson_serial * 100 + attempt,
            grade=grade,
        )
        for q in extra:
            c = allocator.claim(q)
            if c:
                picked.append(c)
            if len(picked) >= count:
                break
        attempt += 1

    return picked[:count]


def question_grounded_in_passage(q: Question, passage: List[str]) -> bool:
    """Kiểm tra đáp án đúng có xuất hiện trong passage hoặc là passage_title."""
    if not passage:
        return False
    blob = " ".join(passage).lower()
    ans = q["choices"][q["answer_index"]].lower()
    prompt = q["prompt"].lower()
    if ans in blob:
        return True
    # title match
    if any(word in ans for word in blob.split() if len(word) > 3):
        return True
    # who names partial
    for w in ans.split():
        if len(w) > 2 and w in blob:
            return True
    # câu đúng là nguyên câu trong passage
    for sent in passage:
        if ans in sent.lower() or sent.lower() in ans:
            return True
    return "chủ yếu nói về" in prompt

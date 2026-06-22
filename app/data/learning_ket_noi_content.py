"""Tạo nội dung micro-bài — phân bổ câu hỏi unique toàn cục."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.data.learning_question_allocator import (
    GlobalQuestionAllocator,
    allocate_lesson_questions,
)
from app.data.learning_reading_passages import build_reading_passage

Question = Dict[str, Any]

# Allocator dùng khi refresh/seed toàn bộ curriculum
_active_allocator: Optional[GlobalQuestionAllocator] = None
_lesson_serial: int = 0


def begin_global_allocation() -> GlobalQuestionAllocator:
    global _active_allocator, _lesson_serial
    _active_allocator = GlobalQuestionAllocator()
    _lesson_serial = 0
    return _active_allocator


def next_lesson_serial() -> int:
    global _lesson_serial
    s = _lesson_serial
    _lesson_serial += 1
    return s


def end_global_allocation() -> None:
    global _active_allocator
    _active_allocator = None


def _questions_for_lesson(
    grade: int,
    subject_slug: str,
    textbook_ref: str,
    chapter: str,
    lesson_title: str,
    idx: int,
) -> List[Question]:
    if _active_allocator is None:
        begin_global_allocation()
    serial = next_lesson_serial()
    return allocate_lesson_questions(
        _active_allocator,
        lesson_serial=serial,
        grade=grade,
        subject_slug=subject_slug,
        textbook_ref=textbook_ref,
        chapter=chapter,
        lesson_title=lesson_title,
        lesson_idx=idx,
    )


def _math_quiz(grade: int, textbook_ref: str, chapter: str, lesson_title: str, idx: int) -> Dict[str, Any]:
    return {"pass_score": 100, "questions": _questions_for_lesson(grade, "toan", textbook_ref, chapter, lesson_title, idx)}


def _knowledge_quiz(
    grade: int, subject_slug: str, textbook_ref: str, chapter: str, lesson_title: str, idx: int
) -> Dict[str, Any]:
    return {"pass_score": 100, "questions": _questions_for_lesson(grade, subject_slug, textbook_ref, chapter, lesson_title, idx)}


def _passage_questions_for_tv(
    grade: int,
    textbook_ref: str,
    chapter: str,
    lesson_title: str,
    idx: int,
    passage: List[str],
    passage_title: str,
) -> List[Question]:
    from app.data.learning_passage_questions import allocate_passage_reading_questions

    if _active_allocator is None:
        begin_global_allocation()
    serial = next_lesson_serial()
    return allocate_passage_reading_questions(
        _active_allocator,
        passage=passage,
        passage_title=passage_title,
        textbook_ref=textbook_ref,
        lesson_title=lesson_title,
        lesson_serial=serial,
        grade=grade,
    )


def _tieng_viet_quiz(
    grade: int, textbook_ref: str, chapter: str, lesson_title: str, idx: int
) -> Dict[str, Any]:
    passage_data = build_reading_passage(chapter, lesson_title, idx, grade=grade)
    topic = passage_data["passage_title"]
    qs = _passage_questions_for_tv(
        grade, textbook_ref, chapter, lesson_title, idx, passage_data["passage"], topic
    )
    return {
        "pass_score": 100,
        "_version": passage_data.get("content_version", f"tv-g{grade}-v0"),
        "passage_title": topic,
        "passage": passage_data["passage"],
        "passage_segments": passage_data.get("passage_segments"),
        "blocks": [
            {"emoji": "📖", "text": f"Đọc to đoạn văn «{topic}» bên dưới."},
            {"emoji": "✏️", "text": f"Trả lời {len(qs)} câu kiến thức bên dưới."},
        ],
        "questions": qs,
    }


def build_lesson_content(
    grade: int,
    subject_slug: str,
    textbook_ref: str,
    chapter: str,
    lesson_title: str,
    idx: int,
) -> Dict[str, Any]:
    if subject_slug == "toan":
        return _math_quiz(grade, textbook_ref, chapter, lesson_title, idx)
    if subject_slug == "tieng-viet":
        return _tieng_viet_quiz(grade, textbook_ref, chapter, lesson_title, idx)
    return _knowledge_quiz(grade, subject_slug, textbook_ref, chapter, lesson_title, idx)


def lesson_content_type(subject_slug: str) -> str:
    if subject_slug == "tieng-viet":
        return "read"
    return "quiz"

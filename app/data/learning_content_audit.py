"""Phase 0 — audit trạng thái nội dung bài học."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.data.learning_ket_noi_curriculum import SUBJECT_TEMPLATES, chapters_for_subject
from app.data.learning_passage_questions import question_grounded_in_passage
from app.data.learning_reading_passages import content_version_for_grade

# Trạng thái nội dung theo phase roadmap
PHASE_STATUS = {
    "tieng-viet": {1: "phase1", 2: "phase2", 3: "phase3", 4: "phase3", 5: "phase3"},
    "toan": {g: "phase4" if g <= 2 else "phase5" for g in range(1, 6)},
    "dao-duc": {g: "phase6" for g in range(1, 4)},
    "tn-xh": {g: "phase6" for g in range(1, 4)},
    "lich-su-dia-ly": {4: "phase7", 5: "phase7"},
    "khoa-hoc": {4: "phase7", 5: "phase7"},
}


def _lesson_status(content: Optional[Dict[str, Any]], slug: str, grade: int) -> str:
    if not content:
        return "missing"
    if slug == "tieng-viet":
        passage = content.get("passage") or []
        ver = content.get("_version") or content.get("content_version") or ""
        expected = content_version_for_grade(grade)
        qs = content.get("questions") or []
        grounded = passage and qs and all(question_grounded_in_passage(q, passage) for q in qs)
        if ver == expected and len(passage) >= 3 and grounded:
            return "ok"
        if passage and len(passage) >= 3 and not grounded:
            return "stale_quiz"
        if ver == expected and len(passage) >= 3:
            return "ok_passage_only"
        if passage and len(passage) >= 3:
            return "stale_version"
        if passage:
            return "short_passage"
        return "no_passage"
    qs = content.get("questions") or []
    blocks = content.get("blocks") or []
    if slug == "toan" and not blocks:
        return "quiz_only"
    if qs:
        return "quiz_ok"
    return "placeholder"


def audit_content_matrix(session: Optional[Session] = None) -> Dict[str, Any]:
    """Ma trận grade × môn × bài — Phase 0 inventory."""
    rows: List[Dict[str, Any]] = []
    summary: Dict[str, int] = {}

    db_lessons: Dict[str, Dict[str, Any]] = {}
    if session is not None:
        from app.models.learning import LearningChapter, LearningLesson, LearningSubject

        for les, ch, sub in (
            session.query(LearningLesson, LearningChapter, LearningSubject)
            .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
            .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
            .all()
        ):
            db_lessons[les.id] = {
                "content": les.content_json,
                "content_type": les.content_type,
                "title": les.title,
                "chapter": ch.name,
                "subject_id": sub.id,
                "grade": sub.grade,
            }

    for grade, subjects in SUBJECT_TEMPLATES.items():
        for slug, name, _icon, _desc, _sort in subjects:
            chapters = chapters_for_subject(grade, slug)
            phase = PHASE_STATUS.get(slug, {}).get(grade, "phase8")
            for ch_name, _sub, ref, lesson_titles in chapters:
                for li, lt in enumerate(lesson_titles):
                    title = f"Bài {li + 1}: {lt}"
                    status = "planned"
                    if session is not None:
                        match = next(
                            (
                                v
                                for v in db_lessons.values()
                                if v["grade"] == grade and v["title"] == title and v["chapter"] == ch_name
                            ),
                            None,
                        )
                        if match:
                            status = _lesson_status(match["content"], slug, grade)
                    rows.append(
                        {
                            "grade": grade,
                            "subject": slug,
                            "subject_name": name,
                            "chapter": ch_name,
                            "lesson": title,
                            "textbook_ref": ref,
                            "phase": phase,
                            "status": status,
                        }
                    )
                    summary[status] = summary.get(status, 0) + 1

    return {
        "total_slots": len(rows),
        "summary": summary,
        "rows": rows,
    }


_MATRIX_FIELDS = [
    "grade",
    "subject",
    "subject_name",
    "chapter",
    "lesson",
    "textbook_ref",
    "phase",
    "status",
]


def export_matrix_csv(session: Session, path: str) -> int:
    """Xuất ma trận audit ra CSV — Phase 0 deliverable."""
    import csv

    data = audit_content_matrix(session)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_MATRIX_FIELDS)
        w.writeheader()
        for row in data["rows"]:
            w.writerow({k: row[k] for k in _MATRIX_FIELDS})
    return len(data["rows"])

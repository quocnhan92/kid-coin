"""Summer learning path — catalog, progress, parent overview."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.learning import (
    LearningChapter,
    LearningChapterProgress,
    LearningDailySummary,
    LearningLesson,
    LearningLessonProgress,
    LearningLessonStep,
    LearningSubject,
)
from app.models.user_family import Role, User

GRADE_META = {
    1: {"label": "Lớp Một", "color_primary": "#E85D24", "color_bg": "#FAECE7", "color_dark": "#993C1D"},
    2: {"label": "Lớp Hai", "color_primary": "#D4537E", "color_bg": "#FBEAF0", "color_dark": "#72243E"},
    3: {"label": "Lớp Ba", "color_primary": "#639922", "color_bg": "#EAF3DE", "color_dark": "#27500A"},
    4: {"label": "Lớp Bốn", "color_primary": "#185FA5", "color_bg": "#E6F1FB", "color_dark": "#0C447C"},
    5: {"label": "Lớp Năm", "color_primary": "#7F77DD", "color_bg": "#EEEDFE", "color_dark": "#3C3489"},
}


def _stars_from_score(score: int) -> int:
    if score >= 90:
        return 3
    if score >= 70:
        return 2
    if score >= 60:
        return 1
    return 0


def _chapter_status(completed: int, total: int, has_partial: bool) -> str:
    if total == 0:
        return "empty"
    if completed >= total:
        return "done"
    if completed > 0 or has_partial:
        return "partial"
    return "empty"


def resolve_kid(db: Session, current_user: User, kid_id: Optional[UUID] = None) -> User:
    if current_user.role == Role.KID:
        return current_user
    if current_user.role == Role.PARENT:
        if kid_id:
            kid = (
                db.query(User)
                .filter(User.id == kid_id, User.family_id == current_user.family_id, User.role == Role.KID)
                .first()
            )
            if not kid:
                raise HTTPException(status_code=404, detail="Kid not found")
            return kid
        kid = (
            db.query(User)
            .filter(User.family_id == current_user.family_id, User.role == Role.KID, User.is_deleted.is_(False))
            .first()
        )
        if not kid:
            raise HTTPException(status_code=404, detail="No kid in family")
        return kid
    raise HTTPException(status_code=403, detail="Not allowed")


def infer_grade(kid: User) -> int:
    if kid.birth_date:
        today = date.today()
        age = today.year - kid.birth_date.year - (
            (today.month, today.day) < (kid.birth_date.month, kid.birth_date.day)
        )
        if 6 <= age <= 7:
            return 1
        if 7 <= age <= 8:
            return 2
        if 8 <= age <= 9:
            return 3
        if 9 <= age <= 10:
            return 4
        if 10 <= age <= 11:
            return 5
    return 1


def list_grades() -> List[Dict[str, Any]]:
    return [
        {"grade": g, "label": meta["label"], "stars_hint": "⭐⭐⭐", **meta}
        for g, meta in GRADE_META.items()
    ]


def _subject_progress(
    db: Session, kid_id: UUID, subject_id: str
) -> Tuple[int, int, int]:
    chapters = (
        db.query(LearningChapter)
        .filter(LearningChapter.subject_id == subject_id, LearningChapter.is_published.is_(True))
        .all()
    )
    if not chapters:
        return 0, 0, 0
    chapter_ids = [c.id for c in chapters]
    rows = (
        db.query(LearningChapterProgress)
        .filter(
            LearningChapterProgress.user_id == kid_id,
            LearningChapterProgress.chapter_id.in_(chapter_ids),
        )
        .all()
    )
    by_id = {r.chapter_id: r for r in rows}
    done = partial = 0
    for ch in chapters:
        st = by_id.get(ch.id)
        if st and st.status == "done":
            done += 1
        elif st and st.status == "partial":
            partial += 1
    total = len(chapters)
    effective = done + partial * 0.5
    pct = round((effective / total) * 100) if total else 0
    return pct, done, total


def list_subjects(db: Session, grade: int, kid: User) -> Dict[str, Any]:
    subjects = (
        db.query(LearningSubject)
        .filter(LearningSubject.grade == grade, LearningSubject.is_active.is_(True))
        .order_by(LearningSubject.sort_order, LearningSubject.name)
        .all()
    )
    items = []
    for s in subjects:
        pct, done, total = _subject_progress(db, kid.id, s.id)
        items.append(
            {
                "id": s.id,
                "name": s.name,
                "icon": s.icon,
                "description": s.description,
                "is_required": s.is_required,
                "color_primary": s.color_primary,
                "color_bg": s.color_bg,
                "color_dark": s.color_dark,
                "progress_pct": pct,
                "chapters_done": done,
                "chapters_total": total,
            }
        )
    return {"grade": grade, "subjects": items}


def list_teacher_lessons(db: Session, grade: int, kid: User) -> Dict[str, Any]:
    """Toàn bộ bài học đã publish theo lớp — dùng cho khung Giáo viên online."""
    rows = (
        db.query(LearningLesson, LearningChapter, LearningSubject)
        .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
        .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
        .filter(
            LearningSubject.grade == grade,
            LearningSubject.is_active.is_(True),
            LearningLesson.is_published.is_(True),
        )
        .order_by(
            LearningSubject.sort_order,
            LearningChapter.sort_index,
            LearningLesson.sort_index,
            LearningLesson.title,
        )
        .all()
    )
    if not rows:
        return {"grade": grade, "total": 0, "lessons": []}

    lesson_ids = [les.id for les, _, _ in rows]
    prog_rows = (
        db.query(LearningLessonProgress)
        .filter(
            LearningLessonProgress.user_id == kid.id,
            LearningLessonProgress.lesson_id.in_(lesson_ids),
        )
        .all()
    )
    prog_by_id = {r.lesson_id: r for r in prog_rows}

    guided_ids = [les.id for les, _, _ in rows if les.content_type == "guided"]
    step_counts: Dict[Any, int] = {}
    if guided_ids:
        step_counts = dict(
            db.query(LearningLessonStep.lesson_id, func.count(LearningLessonStep.id))
            .filter(LearningLessonStep.lesson_id.in_(guided_ids))
            .group_by(LearningLessonStep.lesson_id)
            .all()
        )

    items = []
    for les, ch, sub in rows:
        prog = prog_by_id.get(les.id)
        status = prog.status if prog else "not_started"
        step_count = int(step_counts.get(les.id, 0))
        if les.content_type != "guided" and les.content_json:
            qs = (les.content_json or {}).get("questions") or []
            step_count = len(qs) if qs else step_count
        items.append(
            {
                "id": les.id,
                "title": les.title,
                "summary": les.summary,
                "duration_min": les.duration_min,
                "content_type": les.content_type,
                "subject_id": sub.id,
                "subject_name": sub.name,
                "subject_icon": sub.icon,
                "chapter_name": ch.name,
                "status": status,
                "stars": prog.stars if prog else 0,
                "step_count": step_count,
                "progress_emoji": les.progress_emoji or ("🎓" if les.content_type == "guided" else "📖"),
                "already_completed": status == "completed",
                "sort_index": les.sort_index,
            }
        )
    return {"grade": grade, "total": len(items), "lessons": items}


def get_subject_map(db: Session, subject_id: str, kid: User) -> Dict[str, Any]:
    subject = db.query(LearningSubject).filter(LearningSubject.id == subject_id).first()
    if not subject or not subject.is_active:
        raise HTTPException(status_code=404, detail="Subject not found")

    chapters = (
        db.query(LearningChapter)
        .filter(LearningChapter.subject_id == subject_id, LearningChapter.is_published.is_(True))
        .order_by(LearningChapter.sort_index, LearningChapter.name)
        .all()
    )
    chapter_ids = [c.id for c in chapters]
    progress_rows = (
        db.query(LearningChapterProgress)
        .filter(
            LearningChapterProgress.user_id == kid.id,
            LearningChapterProgress.chapter_id.in_(chapter_ids),
        )
        .all()
        if chapter_ids
        else []
    )
    prog_by_id = {r.chapter_id: r for r in progress_rows}

    lesson_counts = dict(
        db.query(LearningLesson.chapter_id, func.count(LearningLesson.id))
        .filter(LearningLesson.chapter_id.in_(chapter_ids), LearningLesson.is_published.is_(True))
        .group_by(LearningLesson.chapter_id)
        .all()
        if chapter_ids
        else []
    )

    done = partial = 0
    chapter_items = []
    for ch in chapters:
        prog = prog_by_id.get(ch.id)
        status = prog.status if prog else "empty"
        stars = prog.stars if prog else 0
        if status == "done":
            done += 1
        elif status == "partial":
            partial += 1
        chapter_items.append(
            {
                "id": ch.id,
                "name": ch.name,
                "subtitle": ch.subtitle,
                "sort_index": ch.sort_index,
                "status": status,
                "stars": stars,
                "est_minutes": ch.est_minutes,
                "lesson_count": lesson_counts.get(ch.id, 0),
            }
        )

    total = len(chapters)
    effective = done + partial * 0.5
    pct = round((effective / total) * 100) if total else 0

    return {
        "subject": {
            "id": subject.id,
            "name": subject.name,
            "icon": subject.icon,
            "grade": subject.grade,
            "description": subject.description,
            "color_primary": subject.color_primary,
            "color_bg": subject.color_bg,
            "color_dark": subject.color_dark,
        },
        "overall": {"done": done, "partial": partial, "total": total, "progress_pct": pct},
        "chapters": chapter_items,
    }


def list_chapter_lessons(db: Session, chapter_id: UUID, kid: User) -> Dict[str, Any]:
    chapter = db.query(LearningChapter).filter(LearningChapter.id == chapter_id).first()
    if not chapter or not chapter.is_published:
        raise HTTPException(status_code=404, detail="Chapter not found")

    subject = db.query(LearningSubject).filter(LearningSubject.id == chapter.subject_id).first()
    lessons = (
        db.query(LearningLesson)
        .filter(LearningLesson.chapter_id == chapter_id, LearningLesson.is_published.is_(True))
        .order_by(LearningLesson.sort_index, LearningLesson.title)
        .all()
    )
    lesson_ids = [l.id for l in lessons]
    prog_rows = (
        db.query(LearningLessonProgress)
        .filter(
            LearningLessonProgress.user_id == kid.id,
            LearningLessonProgress.lesson_id.in_(lesson_ids),
        )
        .all()
        if lesson_ids
        else []
    )
    prog_by_id = {r.lesson_id: r for r in prog_rows}

    items = []
    for les in lessons:
        prog = prog_by_id.get(les.id)
        status = prog.status if prog else "not_started"
        items.append(
            {
                "id": les.id,
                "title": les.title,
                "summary": les.summary,
                "duration_min": les.duration_min,
                "content_type": les.content_type,
                "status": status,
                "stars": prog.stars if prog else 0,
                "sort_index": les.sort_index,
                "already_completed": status == "completed",
            }
        )

    return {
        "chapter": {
            "id": chapter.id,
            "name": chapter.name,
            "subtitle": chapter.subtitle,
            "subject_id": chapter.subject_id,
            "subject_name": subject.name if subject else "",
        },
        "lessons": items,
    }


def get_lesson_content(db: Session, lesson_id: UUID, kid: User) -> Dict[str, Any]:
    lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not lesson or not lesson.is_published:
        raise HTTPException(status_code=404, detail="Lesson not found")
    prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid.id, LearningLessonProgress.lesson_id == lesson_id)
        .first()
    )
    already = bool(prog and prog.status == "completed")
    return {
        "id": lesson.id,
        "title": lesson.title,
        "duration_min": lesson.duration_min,
        "content_type": lesson.content_type,
        "content": lesson.content_json or {},
        "already_completed": already,
        "is_replay": already,
    }


def _ensure_chapter_progress(
    db: Session, kid_id: UUID, chapter_id: UUID, total_lessons: int
) -> LearningChapterProgress:
    row = (
        db.query(LearningChapterProgress)
        .filter(
            LearningChapterProgress.user_id == kid_id,
            LearningChapterProgress.chapter_id == chapter_id,
        )
        .first()
    )
    if not row:
        row = LearningChapterProgress(
            user_id=kid_id,
            chapter_id=chapter_id,
            total_lessons=total_lessons,
        )
        db.add(row)
    elif row.total_lessons != total_lessons:
        row.total_lessons = total_lessons
    return row


def _recompute_chapter(chapter_prog: LearningChapterProgress, lesson_rows: List[LearningLessonProgress]) -> None:
    completed = sum(1 for r in lesson_rows if r.status == "completed")
    has_partial = any(r.status == "in_progress" for r in lesson_rows)
    chapter_prog.lessons_completed = completed
    chapter_prog.status = _chapter_status(completed, chapter_prog.total_lessons, has_partial)
    if lesson_rows:
        chapter_prog.stars = min(
            3,
            max((r.stars for r in lesson_rows if r.status == "completed"), default=0),
        )
    chapter_prog.last_studied_at = datetime.now(timezone.utc)


def _bump_daily(db: Session, kid_id: UUID, minutes: int, lessons: int, chapters: int = 1) -> LearningDailySummary:
    today = date.today()
    row = (
        db.query(LearningDailySummary)
        .filter(LearningDailySummary.user_id == kid_id, LearningDailySummary.study_date == today)
        .first()
    )
    if not row:
        row = LearningDailySummary(user_id=kid_id, study_date=today)
        db.add(row)
    row.minutes_studied = (row.minutes_studied or 0) + minutes
    row.lessons_completed = (row.lessons_completed or 0) + lessons
    row.chapters_touched = (row.chapters_touched or 0) + chapters
    return row


def bump_step_daily(db: Session, kid_id: UUID) -> None:
    today = date.today()
    row = (
        db.query(LearningDailySummary)
        .filter(LearningDailySummary.user_id == kid_id, LearningDailySummary.study_date == today)
        .first()
    )
    if not row:
        row = LearningDailySummary(user_id=kid_id, study_date=today)
        db.add(row)
    row.steps_completed = (row.steps_completed or 0) + 1


def bump_checkpoint_daily(db: Session, kid_id: UUID) -> None:
    today = date.today()
    row = (
        db.query(LearningDailySummary)
        .filter(LearningDailySummary.user_id == kid_id, LearningDailySummary.study_date == today)
        .first()
    )
    if not row:
        row = LearningDailySummary(user_id=kid_id, study_date=today)
        db.add(row)
    row.checkpoints_confirmed = (row.checkpoints_confirmed or 0) + 1


def _all_answers_correct(content: dict, answers: List[Dict[str, Any]]) -> bool:
    questions = list(content.get("questions") or [])
    if not questions and content.get("check_question"):
        questions = [content["check_question"]]
    if not questions:
        return True
    if len(answers) < len(questions):
        return False
    for i, q in enumerate(questions):
        a = answers[i] if i < len(answers) else None
        if not a or a.get("selected") != q.get("answer_index"):
            return False
    return True


def complete_lesson(
    db: Session,
    lesson_id: UUID,
    kid: User,
    score: int,
    time_spent_sec: int,
    answers: List[Dict[str, Any]],
    guided_mode: bool = False,
) -> Dict[str, Any]:
    lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not lesson or not lesson.is_published:
        raise HTTPException(status_code=404, detail="Lesson not found")

    chapter = db.query(LearningChapter).filter(LearningChapter.id == lesson.chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    all_lessons = (
        db.query(LearningLesson)
        .filter(LearningLesson.chapter_id == chapter.id, LearningLesson.is_published.is_(True))
        .all()
    )
    total = len(all_lessons)
    lesson_ids = [l.id for l in all_lessons]

    lesson_prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid.id, LearningLessonProgress.lesson_id == lesson_id)
        .first()
    )
    if not lesson_prog:
        lesson_prog = LearningLessonProgress(user_id=kid.id, lesson_id=lesson_id)
        db.add(lesson_prog)

    was_completed = lesson_prog.status == "completed"
    stars = _stars_from_score(score)
    content = lesson.content_json or {}
    if guided_mode:
        passed = score >= 60
    else:
        passed = _all_answers_correct(content, answers) and score >= 100

    lesson_prog.attempts = (lesson_prog.attempts or 0) + 1
    lesson_prog.time_spent_sec = (lesson_prog.time_spent_sec or 0) + time_spent_sec

    # Học lại: không cập nhật điểm/sao/thống kê ngày như lần đầu
    if was_completed:
        if not passed:
            db.commit()
            db.refresh(lesson_prog)
            return {
                "lesson": {
                    "status": lesson_prog.status,
                    "stars": lesson_prog.stars,
                    "score": lesson_prog.score,
                },
                "chapter": {"status": "done", "stars": 0, "lessons_completed": 0, "total_lessons": total},
                "daily": {
                    "study_date": date.today(),
                    "minutes_studied": 0,
                    "lessons_completed": 0,
                },
                "replay": True,
            }
        prev = lesson_prog.answers_json if isinstance(lesson_prog.answers_json, dict) else {}
        replays = list(prev.get("replays") or [])
        replays.append(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "score": score,
                "guided": guided_mode,
            }
        )
        lesson_prog.answers_json = {**prev, "last_replay": answers, "replays": replays[-30:]}
        db.commit()
        db.refresh(lesson_prog)
        chapter_prog = (
            db.query(LearningChapterProgress)
            .filter(
                LearningChapterProgress.user_id == kid.id,
                LearningChapterProgress.chapter_id == chapter.id,
            )
            .first()
        )
        daily = (
            db.query(LearningDailySummary)
            .filter(LearningDailySummary.user_id == kid.id, LearningDailySummary.study_date == date.today())
            .first()
        )
        return {
            "lesson": {
                "status": lesson_prog.status,
                "stars": lesson_prog.stars,
                "score": lesson_prog.score,
            },
            "chapter": {
                "status": chapter_prog.status if chapter_prog else "empty",
                "stars": chapter_prog.stars if chapter_prog else 0,
                "lessons_completed": chapter_prog.lessons_completed if chapter_prog else 0,
                "total_lessons": chapter_prog.total_lessons if chapter_prog else total,
            },
            "daily": {
                "study_date": date.today(),
                "minutes_studied": daily.minutes_studied if daily else 0,
                "lessons_completed": daily.lessons_completed if daily else 0,
            },
            "replay": True,
        }

    lesson_prog.score = max(lesson_prog.score or 0, score)
    lesson_prog.answers_json = {"last": answers}
    if guided_mode:
        lesson_prog.steps_summary = {"score": score, "steps": answers}
    if passed:
        lesson_prog.status = "completed"
        lesson_prog.stars = max(lesson_prog.stars or 0, stars)
        lesson_prog.completed_at = datetime.now(timezone.utc)
    else:
        lesson_prog.status = "in_progress"
        lesson_prog.stars = max(lesson_prog.stars or 0, stars)

    chapter_prog = _ensure_chapter_progress(db, kid.id, chapter.id, total)
    db.flush()
    all_prog = (
        db.query(LearningLessonProgress)
        .filter(
            LearningLessonProgress.user_id == kid.id,
            LearningLessonProgress.lesson_id.in_(lesson_ids),
        )
        .all()
    )
    _recompute_chapter(chapter_prog, all_prog)

    minutes = max(1, round(time_spent_sec / 60))
    daily = _bump_daily(db, kid.id, minutes, 1 if passed else 0, 0)

    db.commit()
    db.refresh(lesson_prog)
    db.refresh(chapter_prog)
    db.refresh(daily)

    return {
        "lesson": {"status": lesson_prog.status, "stars": lesson_prog.stars, "score": lesson_prog.score},
        "chapter": {
            "status": chapter_prog.status,
            "stars": chapter_prog.stars,
            "lessons_completed": chapter_prog.lessons_completed,
            "total_lessons": chapter_prog.total_lessons,
        },
        "daily": {
            "study_date": daily.study_date,
            "minutes_studied": daily.minutes_studied,
            "lessons_completed": daily.lessons_completed,
        },
        "replay": False,
    }


def get_today_summary(db: Session, kid: User) -> Dict[str, Any]:
    today = date.today()
    row = (
        db.query(LearningDailySummary)
        .filter(LearningDailySummary.user_id == kid.id, LearningDailySummary.study_date == today)
        .first()
    )
    return {
        "minutes_studied": row.minutes_studied if row else 0,
        "lessons_completed": row.lessons_completed if row else 0,
        "goal_min": 15,
        "goal_max": 60,
    }


def parent_overview(db: Session, parent: User) -> Dict[str, Any]:
    kids = (
        db.query(User)
        .filter(User.family_id == parent.family_id, User.role == Role.KID, User.is_deleted.is_(False))
        .all()
    )
    today = date.today()
    week_start = today - timedelta(days=6)

    result = []
    for kid in kids:
        today_row = (
            db.query(LearningDailySummary)
            .filter(LearningDailySummary.user_id == kid.id, LearningDailySummary.study_date == today)
            .first()
        )
        week_minutes = (
            db.query(func.coalesce(func.sum(LearningDailySummary.minutes_studied), 0))
            .filter(
                LearningDailySummary.user_id == kid.id,
                LearningDailySummary.study_date >= week_start,
            )
            .scalar()
        ) or 0

        # Tất cả lớp 1–5 — bé tự chọn lớp, không suy từ tuổi
        subjects = (
            db.query(LearningSubject)
            .filter(LearningSubject.grade.between(1, 5), LearningSubject.is_active.is_(True))
            .order_by(LearningSubject.grade, LearningSubject.sort_order)
            .all()
        )
        subj_items = []
        for s in subjects:
            pct, _, _ = _subject_progress(db, kid.id, s.id)
            stars_total = (
                db.query(func.coalesce(func.sum(LearningChapterProgress.stars), 0))
                .join(LearningChapter, LearningChapter.id == LearningChapterProgress.chapter_id)
                .filter(
                    LearningChapterProgress.user_id == kid.id,
                    LearningChapter.subject_id == s.id,
                )
                .scalar()
            ) or 0
            subj_items.append(
                {
                    "subject_id": s.id,
                    "name": f"L{s.grade} · {s.name}",
                    "icon": s.icon,
                    "grade": s.grade,
                    "progress_pct": pct,
                    "stars_total": int(stars_total),
                }
            )

        result.append(
            {
                "kid_id": kid.id,
                "display_name": kid.display_name,
                "today_minutes": today_row.minutes_studied if today_row else 0,
                "week_minutes": int(week_minutes),
                "today_lessons": today_row.lessons_completed if today_row else 0,
                "subjects": subj_items,
            }
        )

    from app.services import learning_player_service

    pending = learning_player_service.list_pending_checkpoints(db, parent)
    return {"kids": result, "pending_checkpoints": pending}


def parent_timeline(db: Session, parent: User, kid_id: UUID, days: int = 7) -> Dict[str, Any]:
    kid = resolve_kid(db, parent, kid_id)
    start = date.today() - timedelta(days=max(1, min(days, 30)) - 1)
    rows = (
        db.query(LearningDailySummary)
        .filter(LearningDailySummary.user_id == kid.id, LearningDailySummary.study_date >= start)
        .order_by(LearningDailySummary.study_date)
        .all()
    )
    return {
        "days": [
            {"date": r.study_date, "minutes": r.minutes_studied, "lessons": r.lessons_completed}
            for r in rows
        ]
    }

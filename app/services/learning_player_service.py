"""Online Teacher player — steps, schedule, family checkpoints."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.learning import (
    LearningChapter,
    LearningDailySummary,
    LearningFamilyCheckpoint,
    LearningGradeSchedule,
    LearningLesson,
    LearningLessonProgress,
    LearningLessonStep,
    LearningScheduleSlot,
    LearningStepProgress,
    LearningSubject,
)
from app.models.user_family import Role, User
from app.services import learning_service

VALID_STEP_TYPES = frozenset(
    {"observe", "listen_read", "write", "choice", "quiz", "family_checkpoint", "reward"}
)
PASSED_STATUSES = frozenset({"passed", "skipped"})


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def levenshtein_ratio(a: str, b: str) -> int:
    a, b = _norm(a), _norm(b)
    if not a and not b:
        return 100
    if not a or not b:
        return 0
    if a == b:
        return 100
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    dist = prev[lb]
    return max(0, round(100 * (1 - dist / max(la, lb))))


def _get_steps(db: Session, lesson_id: UUID) -> List[LearningLessonStep]:
    return (
        db.query(LearningLessonStep)
        .filter(LearningLessonStep.lesson_id == lesson_id)
        .order_by(LearningLessonStep.sort_index)
        .all()
    )


def _step_progress_map(db: Session, kid_id: UUID, step_ids: List[UUID]) -> Dict[UUID, LearningStepProgress]:
    if not step_ids:
        return {}
    rows = (
        db.query(LearningStepProgress)
        .filter(LearningStepProgress.user_id == kid_id, LearningStepProgress.step_id.in_(step_ids))
        .all()
    )
    return {r.step_id: r for r in rows}


def _resume_index(steps: List[LearningLessonStep], prog: Dict[UUID, LearningStepProgress]) -> int:
    for i, s in enumerate(steps):
        row = prog.get(s.id)
        if not row or row.status not in PASSED_STATUSES:
            return i
    return len(steps)


def _progress_emojis(steps: List[LearningLessonStep]) -> List[str]:
    icons = [s.emoji_icon for s in steps if s.emoji_icon]
    return icons if icons else ["🍏", "🍋", "🍇", "🎁"]


def get_lesson_player(db: Session, lesson_id: UUID, kid: User) -> Dict[str, Any]:
    lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not lesson or not lesson.is_published:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if lesson.content_type != "guided":
        raise HTTPException(status_code=400, detail="Lesson is not a guided player lesson")

    steps = _get_steps(db, lesson.id)
    if not steps:
        raise HTTPException(status_code=404, detail="No steps for lesson")

    chapter = db.query(LearningChapter).filter(LearningChapter.id == lesson.chapter_id).first()
    subject = (
        db.query(LearningSubject).filter(LearningSubject.id == chapter.subject_id).first()
        if chapter
        else None
    )
    prog = _step_progress_map(db, kid.id, [s.id for s in steps])
    resume = _resume_index(steps, prog)

    lesson_prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid.id, LearningLessonProgress.lesson_id == lesson_id)
        .first()
    )
    already_completed = bool(lesson_prog and lesson_prog.status == "completed")
    resume = 0 if already_completed else _resume_index(steps, prog)

    return {
        "lesson": {
            "id": lesson.id,
            "title": lesson.title,
            "subject": subject.name if subject else "",
            "duration_min": lesson.duration_min,
            "content_type": lesson.content_type,
            "progress_emojis": _progress_emojis(steps),
            "already_completed": already_completed,
            "is_replay": already_completed,
        },
        "steps": [
            {
                "id": s.id,
                "sort_index": s.sort_index,
                "step_type": s.step_type,
                "emoji_icon": s.emoji_icon,
                "config": s.config_json or {},
                "status": prog[s.id].status if s.id in prog else "not_started",
                "is_required": s.is_required,
            }
            for s in steps
        ],
        "resume_at_step_index": resume,
    }


def _eval_step(
    step: LearningLessonStep, interaction: str, payload: Dict[str, Any]
) -> Tuple[bool, int, Dict[str, Any], Optional[str]]:
    cfg = step.config_json or {}
    stype = step.step_type

    if stype == "observe":
        return True, 100, {}, "success"

    if stype == "reward":
        return True, 100, {}, "success"

    if stype == "choice":
        correct = int(cfg.get("answer_index", 0))
        sel = payload.get("selected_index")
        if sel is None:
            return False, 0, {}, "wrong"
        ok = int(sel) == correct
        return ok, 100 if ok else 0, {"selected_index": sel}, "success" if ok else "wrong"

    if stype == "quiz":
        questions = list(cfg.get("questions") or [])
        if not questions:
            return True, 100, {}, "success"
        answers = list(payload.get("answers") or [])
        if len(answers) < len(questions):
            return False, 0, {}, "wrong"
        for i, q in enumerate(questions):
            a = answers[i] if i < len(answers) else {}
            if a.get("selected") != q.get("answer_index"):
                return False, 0, {}, "wrong"
        return True, 100, {"answers": answers}, "success"

    if stype == "listen_read":
        keywords = list(cfg.get("stt_keywords") or [])
        transcript = _norm(str(payload.get("transcript", "")))
        threshold = int(cfg.get("pass_threshold", 80))
        if cfg.get("keyword_mode", True) and keywords:
            ok = any(_norm(kw) in transcript for kw in keywords if kw)
            return ok, 100 if ok else levenshtein_ratio(transcript, keywords[0]), {"transcript": transcript}, (
                "success" if ok else "wrong"
            )
        expected = _norm(str(cfg.get("display_text", "")))
        ratio = levenshtein_ratio(transcript, expected)
        ok = ratio >= threshold
        return ok, ratio, {"transcript": transcript, "similarity": ratio}, "success" if ok else "wrong"

    if stype == "write":
        correct = int(cfg.get("answer_index", 0))
        sel = payload.get("selected_index")
        if sel is not None:
            ok = int(sel) == correct
            return ok, 100 if ok else 0, {}, "success" if ok else "wrong"
        overlap = int(payload.get("overlap_pct", 0))
        ok = overlap >= int(cfg.get("min_overlap_pct", 60))
        return ok, overlap, {"overlap_pct": overlap}, "success" if ok else "wrong"

    if stype == "family_checkpoint":
        if interaction == "skip":
            return True, 100, {"skipped": True}, "success"
        if interaction == "checkpoint_request":
            return False, 0, {"pending_checkpoint": True}, "waiting_parent"
        return False, 0, {}, "waiting_parent"

    raise HTTPException(status_code=400, detail=f"Unknown step type: {stype}")


def _ensure_step_progress(db: Session, kid_id: UUID, step_id: UUID) -> LearningStepProgress:
    row = (
        db.query(LearningStepProgress)
        .filter(LearningStepProgress.user_id == kid_id, LearningStepProgress.step_id == step_id)
        .first()
    )
    if not row:
        row = LearningStepProgress(user_id=kid_id, step_id=step_id, status="in_progress")
        db.add(row)
    return row


def _create_checkpoint(
    db: Session, kid: User, step: LearningLessonStep, lesson_id: UUID
) -> LearningFamilyCheckpoint:
    existing = (
        db.query(LearningFamilyCheckpoint)
        .filter(
            LearningFamilyCheckpoint.user_id == kid.id,
            LearningFamilyCheckpoint.step_id == step.id,
            LearningFamilyCheckpoint.status == "pending",
        )
        .first()
    )
    if existing:
        return existing
    row = LearningFamilyCheckpoint(
        user_id=kid.id,
        step_id=step.id,
        lesson_id=lesson_id,
        status="pending",
        requested_at=datetime.now(timezone.utc),
    )
    db.add(row)
    return row


def _all_required_passed(steps: List[LearningLessonStep], prog: Dict[UUID, LearningStepProgress]) -> bool:
    for s in steps:
        if not s.is_required:
            continue
        row = prog.get(s.id)
        if not row or row.status not in PASSED_STATUSES:
            return False
    return True


def _complete_guided_lesson(
    db: Session, lesson: LearningLesson, kid: User, time_spent_sec: int
) -> Dict[str, Any]:
    steps = _get_steps(db, lesson.id)
    prog = _step_progress_map(db, kid.id, [s.id for s in steps])
    passed = sum(1 for s in steps if prog.get(s.id) and prog[s.id].status in PASSED_STATUSES)
    score = round(100 * passed / len(steps)) if steps else 100

    answers = []
    for s in steps:
        row = prog.get(s.id)
        if row and row.result_json:
            answers.append({"step_id": str(s.id), "result": row.result_json})

    return learning_service.complete_lesson(
        db, lesson.id, kid, score, time_spent_sec, answers, guided_mode=True
    )


def submit_step(
    db: Session,
    lesson_id: UUID,
    step_id: UUID,
    kid: User,
    interaction: str,
    payload: Dict[str, Any],
    time_spent_sec: int = 0,
) -> Dict[str, Any]:
    lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not lesson or not lesson.is_published or lesson.content_type != "guided":
        raise HTTPException(status_code=404, detail="Guided lesson not found")

    step = (
        db.query(LearningLessonStep)
        .filter(LearningLessonStep.id == step_id, LearningLessonStep.lesson_id == lesson_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    steps = _get_steps(db, lesson.id)
    step_prog = _ensure_step_progress(db, kid.id, step.id)
    step_prog.attempts = (step_prog.attempts or 0) + 1

    lesson_prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid.id, LearningLessonProgress.lesson_id == lesson_id)
        .first()
    )
    is_replay = bool(lesson_prog and lesson_prog.status == "completed")

    ok, score, result_extra, feedback_type = _eval_step(step, interaction, payload or {})
    checkpoint_id = None

    if step.step_type == "family_checkpoint" and feedback_type == "waiting_parent":
        cp = _create_checkpoint(db, kid, step, lesson.id)
        db.flush()
        checkpoint_id = cp.id
        step_prog.status = "in_progress"
        step_prog.result_json = {"checkpoint_id": str(cp.id)}
        db.commit()
        return {
            "step": {"id": step.id, "status": "in_progress", "score": 0},
            "feedback": {
                "type": "waiting_parent",
                "tts_text": "Hãy nhờ bố mẹ bấm xác nhận trên điện thoại nhé!",
                "checkpoint_id": str(checkpoint_id),
            },
            "next_step_index": step.sort_index,
            "lesson_complete": False,
        }

    if not ok and interaction != "skip":
        step_prog.status = "in_progress"
        step_prog.score = max(step_prog.score or 0, score)
        step_prog.result_json = result_extra
        db.commit()
        tts = "Gần đúng rồi, cố lên nhé!"
        if step.step_type == "listen_read":
            tts = "Gần đúng rồi, nghe mẫu và thử lại nhé!"
        return {
            "step": {"id": step.id, "status": "in_progress", "score": score},
            "feedback": {"type": "wrong", "tts_text": tts},
            "next_step_index": step.sort_index,
            "lesson_complete": False,
        }

    step_prog.status = "skipped" if interaction == "skip" else "passed"
    step_prog.score = max(step_prog.score or 0, score)
    step_prog.result_json = result_extra
    step_prog.completed_at = datetime.now(timezone.utc)

    learning_service.bump_step_daily(db, kid.id)

    prog_all = _step_progress_map(db, kid.id, [s.id for s in steps])
    prog_all[step.id] = step_prog
    next_idx = _resume_index(steps, prog_all)
    if is_replay:
        cur_index = next((i for i, s in enumerate(steps) if s.id == step.id), 0)
        lesson_complete = ok and cur_index == len(steps) - 1
    else:
        lesson_complete = _all_required_passed(steps, prog_all)

    complete_payload = None
    if lesson_complete:
        complete_payload = _complete_guided_lesson(db, lesson, kid, max(30, time_spent_sec))
    else:
        db.commit()

    tts = "Xuất sắc quá!"
    if step.step_type == "reward":
        tts = (step.config_json or {}).get("tts_text", tts)

    return {
        "step": {"id": step.id, "status": step_prog.status, "score": step_prog.score},
        "feedback": {
            "type": "success",
            "tts_text": tts,
            "emoji_burst": (step.config_json or {}).get("emoji_burst", ["🎉", "⭐"]),
        },
        "next_step_index": next_idx if not lesson_complete else len(steps),
        "lesson_complete": lesson_complete,
        "completion": complete_payload,
    }


def confirm_checkpoint(db: Session, checkpoint_id: UUID, parent: User) -> Dict[str, Any]:
    cp = db.query(LearningFamilyCheckpoint).filter(LearningFamilyCheckpoint.id == checkpoint_id).first()
    if not cp or cp.status != "pending":
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    kid = db.query(User).filter(User.id == cp.user_id).first()
    if not kid or kid.family_id != parent.family_id:
        raise HTTPException(status_code=403, detail="Not your family")

    cp.status = "confirmed"
    cp.confirmed_by = parent.id
    cp.confirmed_at = datetime.now(timezone.utc)

    step_prog = _ensure_step_progress(db, kid.id, cp.step_id)
    step_prog.status = "passed"
    step_prog.score = 100
    step_prog.completed_at = datetime.now(timezone.utc)
    step_prog.result_json = {"confirmed_by_parent": str(parent.id)}

    lesson = db.query(LearningLesson).filter(LearningLesson.id == cp.lesson_id).first()
    steps = _get_steps(db, cp.lesson_id) if lesson else []
    prog_all = _step_progress_map(db, kid.id, [s.id for s in steps])
    prog_all[cp.step_id] = step_prog

    learning_service.bump_checkpoint_daily(db, kid.id)

    lesson_prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid.id, LearningLessonProgress.lesson_id == cp.lesson_id)
        .first()
    )
    is_replay = bool(lesson_prog and lesson_prog.status == "completed")
    if is_replay:
        last_step = steps[-1] if steps else None
        lesson_complete = bool(last_step and last_step.id == cp.step_id)
    else:
        lesson_complete = lesson and _all_required_passed(steps, prog_all)
    complete_payload = None
    if lesson_complete and lesson:
        complete_payload = _complete_guided_lesson(db, lesson, kid, 60)

    if not lesson_complete:
        db.commit()

    return {
        "ok": True,
        "checkpoint_id": str(cp.id),
        "lesson_complete": lesson_complete,
        "completion": complete_payload,
    }


def list_pending_checkpoints(db: Session, parent: User) -> List[Dict[str, Any]]:
    kids = (
        db.query(User)
        .filter(User.family_id == parent.family_id, User.role == Role.KID, User.is_deleted.is_(False))
        .all()
    )
    kid_ids = [k.id for k in kids]
    if not kid_ids:
        return []

    rows = (
        db.query(LearningFamilyCheckpoint, LearningLesson, User)
        .join(LearningLesson, LearningLesson.id == LearningFamilyCheckpoint.lesson_id)
        .join(User, User.id == LearningFamilyCheckpoint.user_id)
        .filter(
            LearningFamilyCheckpoint.user_id.in_(kid_ids),
            LearningFamilyCheckpoint.status == "pending",
        )
        .order_by(LearningFamilyCheckpoint.requested_at.desc())
        .all()
    )
    return [
        {
            "checkpoint_id": str(cp.id),
            "kid_id": str(kid.id),
            "kid_name": kid.display_name,
            "lesson_id": str(les.id),
            "lesson_title": les.title,
            "requested_at": cp.requested_at.isoformat() if cp.requested_at else None,
        }
        for cp, les, kid in rows
    ]


def _lesson_slot_status(db: Session, kid_id: UUID, lesson_id: Optional[UUID]) -> Tuple[str, int, int]:
    if not lesson_id:
        return "not_started", 0, 0
    les = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not les:
        return "not_started", 0, 0
    if les.content_type == "guided":
        steps = _get_steps(db, les.id)
        prog = _step_progress_map(db, kid_id, [s.id for s in steps])
        passed = sum(1 for s in steps if prog.get(s.id) and prog[s.id].status in PASSED_STATUSES)
        status = "completed" if passed >= sum(1 for s in steps if s.is_required) else (
            "in_progress" if passed > 0 else "not_started"
        )
        return status, passed, len(steps)
    prog = (
        db.query(LearningLessonProgress)
        .filter(LearningLessonProgress.user_id == kid_id, LearningLessonProgress.lesson_id == lesson_id)
        .first()
    )
    return (prog.status if prog else "not_started", 0, 0)


def get_schedule_today(db: Session, grade: int, kid: User) -> Dict[str, Any]:
    today = date.today()
    weekday = today.isoweekday()

    schedule = (
        db.query(LearningGradeSchedule)
        .filter(LearningGradeSchedule.grade == grade, LearningGradeSchedule.is_active.is_(True))
        .order_by(LearningGradeSchedule.week_number)
        .first()
    )

    slots: List[Dict[str, Any]] = []
    if schedule:
        slot_rows = (
            db.query(LearningScheduleSlot)
            .filter(LearningScheduleSlot.schedule_id == schedule.id, LearningScheduleSlot.weekday == weekday)
            .order_by(LearningScheduleSlot.session, LearningScheduleSlot.slot_order)
            .all()
        )
        for sl in slot_rows:
            subj = db.query(LearningSubject).filter(LearningSubject.id == sl.subject_id).first()
            les = (
                db.query(LearningLesson).filter(LearningLesson.id == sl.lesson_id).first()
                if sl.lesson_id
                else None
            )
            status, steps_passed, steps_total = _lesson_slot_status(db, kid.id, sl.lesson_id)
            slots.append(
                {
                    "slot_id": str(sl.id),
                    "session": sl.session,
                    "subject": {
                        "id": subj.id,
                        "name": subj.name,
                        "icon": subj.icon,
                    }
                    if subj
                    else {"id": sl.subject_id, "name": "", "icon": "📚"},
                    "lesson": {
                        "id": str(les.id),
                        "title": les.title,
                        "duration_min": les.duration_min,
                        "content_type": les.content_type,
                        "progress_emoji": les.progress_emoji or "🍏",
                        "status": status,
                        "steps_total": steps_total,
                        "steps_passed": steps_passed,
                    }
                    if les
                    else None,
                }
            )

    if not slots:
        slots = _fallback_schedule_slots(db, grade, kid)

    completed = sum(1 for s in slots if s.get("lesson") and s["lesson"].get("status") == "completed")
    return {
        "date": today.isoformat(),
        "weekday": weekday,
        "week_label": schedule.label if schedule else "Tuần học",
        "slots": slots,
        "daily_goal": {"target_lessons": len(slots), "completed": completed},
    }


def _fallback_schedule_slots(db: Session, grade: int, kid: User) -> List[Dict[str, Any]]:
    """Khi chưa có lịch — gợi ý 4 môn đầu."""
    subjects = (
        db.query(LearningSubject)
        .filter(LearningSubject.grade == grade, LearningSubject.is_active.is_(True))
        .order_by(LearningSubject.sort_order)
        .limit(4)
        .all()
    )
    sessions = ["morning", "morning", "afternoon", "afternoon"]
    out = []
    for i, subj in enumerate(subjects):
        ch = (
            db.query(LearningChapter)
            .filter(LearningChapter.subject_id == subj.id, LearningChapter.is_published.is_(True))
            .order_by(LearningChapter.sort_index)
            .first()
        )
        les = None
        if ch:
            les = (
                db.query(LearningLesson)
                .filter(LearningLesson.chapter_id == ch.id, LearningLesson.is_published.is_(True))
                .order_by(LearningLesson.sort_index)
                .first()
            )
        status, sp, st = _lesson_slot_status(db, kid.id, les.id if les else None)
        out.append(
            {
                "slot_id": f"fallback-{i}",
                "session": sessions[i] if i < len(sessions) else "morning",
                "subject": {"id": subj.id, "name": subj.name, "icon": subj.icon},
                "lesson": {
                    "id": str(les.id),
                    "title": les.title,
                    "duration_min": les.duration_min,
                    "content_type": les.content_type,
                    "progress_emoji": les.progress_emoji or "🍏",
                    "status": status,
                    "steps_total": st,
                    "steps_passed": sp,
                }
                if les
                else None,
            }
        )
    return out

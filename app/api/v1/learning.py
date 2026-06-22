"""Summer learning path API."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user_family import Role, User
from app.schemas import learning as schemas
from app.services import learning_service, learning_player_service

router = APIRouter()


@router.get("/grades", response_model=schemas.GradesResponse)
def list_grades():
    return {"grades": learning_service.list_grades()}


@router.get("/grades/{grade}/subjects", response_model=schemas.SubjectsResponse)
def list_subjects(
    grade: int,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_service.list_subjects(db, grade, kid)


@router.get("/grades/{grade}/teacher-lessons", response_model=schemas.TeacherLessonsResponse)
def list_teacher_lessons(
    grade: int,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_service.list_teacher_lessons(db, grade, kid)


@router.get("/subjects/{subject_id}/map", response_model=schemas.SubjectMapResponse)
def subject_map(
    subject_id: str,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_service.get_subject_map(db, subject_id, kid)


@router.get("/chapters/{chapter_id}/lessons", response_model=schemas.ChapterLessonsResponse)
def chapter_lessons(
    chapter_id: UUID,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_service.list_chapter_lessons(db, chapter_id, kid)


@router.get("/lessons/{lesson_id}", response_model=schemas.LessonContentResponse)
def get_lesson(
    lesson_id: UUID,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_service.get_lesson_content(db, lesson_id, kid)


@router.post("/lessons/{lesson_id}/complete", response_model=schemas.LessonCompleteResponse)
def complete_lesson(
    lesson_id: UUID,
    body: schemas.LessonCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != Role.KID:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Only kids can complete lessons")
    return learning_service.complete_lesson(
        db, lesson_id, current_user, body.score, body.time_spent_sec, body.answers
    )


@router.get("/schedule/today", response_model=schemas.ScheduleTodayResponse)
def schedule_today(
    grade: int = 1,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_player_service.get_schedule_today(db, grade, kid)


@router.get("/lessons/{lesson_id}/player", response_model=schemas.LessonPlayerResponse)
def lesson_player(
    lesson_id: UUID,
    kid_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user, kid_id)
    return learning_player_service.get_lesson_player(db, lesson_id, kid)


@router.post("/lessons/{lesson_id}/steps/{step_id}/submit", response_model=schemas.StepSubmitResponse)
def submit_step(
    lesson_id: UUID,
    step_id: UUID,
    body: schemas.StepSubmitRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != Role.KID:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Only kids can submit steps")
    return learning_player_service.submit_step(
        db,
        lesson_id,
        step_id,
        current_user,
        body.interaction,
        body.payload,
        body.time_spent_sec,
    )


@router.post("/family-checkpoints/{checkpoint_id}/confirm", response_model=schemas.CheckpointConfirmResponse)
def confirm_checkpoint(
    checkpoint_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role(Role.PARENT)),
):
    return learning_player_service.confirm_checkpoint(db, checkpoint_id, current_user)


@router.get("/parent/checkpoints/pending")
def parent_pending_checkpoints(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role(Role.PARENT)),
):
    return learning_player_service.list_pending_checkpoints(db, current_user)


@router.get("/me/today", response_model=schemas.TodaySummaryResponse)
def today_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    kid = learning_service.resolve_kid(db, current_user)
    return learning_service.get_today_summary(db, kid)


@router.get("/parent/overview", response_model=schemas.ParentOverviewResponse)
def parent_overview(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role(Role.PARENT)),
):
    return learning_service.parent_overview(db, current_user)


@router.get("/parent/kids/{kid_id}/timeline", response_model=schemas.ParentTimelineResponse)
def parent_timeline(
    kid_id: UUID,
    days: int = 7,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role(Role.PARENT)),
):
    return learning_service.parent_timeline(db, current_user, kid_id, days)

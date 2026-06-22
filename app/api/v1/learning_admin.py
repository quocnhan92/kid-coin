"""Admin CRUD for learning curriculum."""

from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.learning import LearningChapter, LearningLesson, LearningLessonStep, LearningSubject
from app.schemas import learning as schemas

router = APIRouter()


@router.get("/subjects", response_model=List[schemas.SubjectItem])
def admin_list_subjects(
    grade: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    q = db.query(LearningSubject)
    if grade is not None:
        q = q.filter(LearningSubject.grade == grade)
    rows = q.order_by(LearningSubject.grade, LearningSubject.sort_order).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "icon": r.icon,
            "description": r.description,
            "is_required": r.is_required,
            "color_primary": r.color_primary,
            "color_bg": r.color_bg,
            "color_dark": r.color_dark,
            "progress_pct": 0,
            "chapters_done": 0,
            "chapters_total": 0,
        }
        for r in rows
    ]


@router.post("/subjects", response_model=schemas.SubjectItem)
def admin_create_subject(
    body: schemas.AdminSubjectCreate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    if db.query(LearningSubject).filter(LearningSubject.id == body.id).first():
        raise HTTPException(status_code=409, detail="Subject id exists")
    row = LearningSubject(**body.model_dump(), textbook_series="ket_noi_tri_thuc", is_active=True)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "name": row.name,
        "icon": row.icon,
        "description": row.description,
        "is_required": row.is_required,
        "color_primary": row.color_primary,
        "color_bg": row.color_bg,
        "color_dark": row.color_dark,
        "progress_pct": 0,
        "chapters_done": 0,
        "chapters_total": 0,
    }


@router.put("/subjects/{subject_id}")
def admin_update_subject(
    subject_id: str,
    body: schemas.AdminSubjectUpdate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningSubject).filter(LearningSubject.id == subject_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return {"ok": True}


@router.get("/subjects/{subject_id}/chapters")
def admin_list_chapters(
    subject_id: str,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    rows = (
        db.query(LearningChapter)
        .filter(LearningChapter.subject_id == subject_id)
        .order_by(LearningChapter.sort_index)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "subtitle": r.subtitle,
            "sort_index": r.sort_index,
            "est_minutes": r.est_minutes,
            "textbook_ref": r.textbook_ref,
            "is_published": r.is_published,
        }
        for r in rows
    ]


@router.post("/chapters")
def admin_create_chapter(
    body: schemas.AdminChapterCreate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = LearningChapter(**body.model_dump(), is_published=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": str(row.id)}


@router.put("/chapters/{chapter_id}")
def admin_update_chapter(
    chapter_id: UUID,
    body: schemas.AdminChapterUpdate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningChapter).filter(LearningChapter.id == chapter_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return {"ok": True}


@router.get("/chapters/{chapter_id}/lessons")
def admin_list_lessons(
    chapter_id: UUID,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    rows = (
        db.query(LearningLesson)
        .filter(LearningLesson.chapter_id == chapter_id)
        .order_by(LearningLesson.sort_index)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "summary": r.summary,
            "sort_index": r.sort_index,
            "duration_min": r.duration_min,
            "content_type": r.content_type,
            "content_json": r.content_json,
            "is_published": r.is_published,
        }
        for r in rows
    ]


@router.post("/lessons")
def admin_create_lesson(
    body: schemas.AdminLessonCreate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = LearningLesson(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": str(row.id)}


@router.put("/lessons/{lesson_id}")
def admin_update_lesson(
    lesson_id: UUID,
    body: schemas.AdminLessonUpdate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return {"ok": True}


@router.post("/chapters/{chapter_id}/publish")
def admin_publish_chapter(
    chapter_id: UUID,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningChapter).filter(LearningChapter.id == chapter_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    row.is_published = True
    db.query(LearningLesson).filter(LearningLesson.chapter_id == chapter_id).update(
        {"is_published": True}
    )
    db.commit()
    return {"ok": True}


@router.get("/lessons/{lesson_id}/steps")
def admin_list_steps(
    lesson_id: UUID,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    rows = (
        db.query(LearningLessonStep)
        .filter(LearningLessonStep.lesson_id == lesson_id)
        .order_by(LearningLessonStep.sort_index)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "sort_index": r.sort_index,
            "step_type": r.step_type,
            "emoji_icon": r.emoji_icon,
            "config_json": r.config_json,
            "est_seconds": r.est_seconds,
            "is_required": r.is_required,
        }
        for r in rows
    ]


@router.post("/lessons/{lesson_id}/steps")
def admin_create_step(
    lesson_id: UUID,
    body: schemas.AdminStepCreate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    row = LearningLessonStep(id=uuid4(), lesson_id=lesson_id, **body.model_dump())
    db.add(row)
    lesson.content_type = "guided"
    db.commit()
    db.refresh(row)
    return {"id": str(row.id)}


@router.put("/steps/{step_id}")
def admin_update_step(
    step_id: UUID,
    body: schemas.AdminStepUpdate,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningLessonStep).filter(LearningLessonStep.id == step_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return {"ok": True}


@router.delete("/steps/{step_id}")
def admin_delete_step(
    step_id: UUID,
    db: Session = Depends(deps.get_db),
    _admin=Depends(deps.get_current_admin),
):
    row = db.query(LearningLessonStep).filter(LearningLessonStep.id == step_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

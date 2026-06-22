"""Seed curriculum — delegates to SGK Kết nối tri thức G1–G5."""

from sqlalchemy.orm import Session

from app.data.learning_ket_noi_curriculum import seed_ket_noi_curriculum


def seed_learning_curriculum(db: Session) -> None:
    from app.models.learning import LearningSubject
    from app.data.learning_grades_guided_seed import seed_all_guided_lessons

    if db.query(LearningSubject).count() == 0:
        seed_ket_noi_curriculum(db)
    seed_all_guided_lessons(db)
    db.commit()

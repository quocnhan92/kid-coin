"""Migration pre-Phase3: passage-grounded TV questions G1/G2

Revision ID: 027_passage_questions
Revises: 026_tv_g1_g2_passages
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "027_passage_questions"
down_revision: Union[str, None] = "026_tv_g1_g2_passages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content
        from app.data.learning_passage_questions import question_grounded_in_passage
        from app.data.learning_question_allocator import audit_duplicates
        from app.data.passages import tv_g1, tv_g2
        from app.models.learning import LearningChapter, LearningLesson, LearningSubject

        n = refresh_all_lesson_content(session)

        for sid, ver in (("tieng-viet-g1", tv_g1.CONTENT_VERSION), ("tieng-viet-g2", tv_g2.CONTENT_VERSION)):
            lessons = (
                session.query(LearningLesson)
                .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
                .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
                .filter(LearningSubject.id == sid)
                .all()
            )
            for les in lessons:
                cj = les.content_json or {}
                assert cj.get("_version") == ver, f"{sid} {les.title} version mismatch"
                passage = cj.get("passage") or []
                qs = cj.get("questions") or []
                assert len(passage) >= 3, f"{sid} {les.title} short passage"
                assert len(qs) == 3, f"{sid} {les.title} need 3 questions"
                for q in qs:
                    assert question_grounded_in_passage(q, passage), f"ungrounded: {q.get('prompt')}"

        contents = [les.content_json or {} for les in session.query(LearningLesson).all()]
        dups = audit_duplicates(contents)
        if dups:
            raise RuntimeError(f"Duplicate prompts: {len(dups)}")

        session.commit()
        print(f"Passage questions v2: refreshed {n} lessons, TV G1/G2 grounded OK")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    pass

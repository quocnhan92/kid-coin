"""TV G1/G2 passage banks + content_version — Phase 1–2

Revision ID: 026_tv_g1_g2_passages
Revises: 025_reading_passages
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "026_tv_g1_g2_passages"
down_revision: Union[str, None] = "025_reading_passages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_content import build_lesson_content
        from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content
        from app.data.learning_question_allocator import audit_duplicates
        from app.models.learning import LearningChapter, LearningLesson, LearningSubject

        n = refresh_all_lesson_content(session)
        for sid, ver in (("tieng-viet-g1", "tv-g1-v1"), ("tieng-viet-g2", "tv-g2-v1")):
            les = (
                session.query(LearningLesson)
                .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
                .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
                .filter(LearningSubject.id == sid, LearningLesson.sort_index == 0)
                .first()
            )
            if les:
                cj = les.content_json or {}
                assert len(cj.get("passage") or []) >= 3, f"{sid} missing passage"
                assert cj.get("_version") == ver, f"{sid} version {cj.get('_version')} != {ver}"

        g1 = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
        g2 = build_lesson_content(2, "tieng-viet", "G2-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
        assert g1["passage"] != g2["passage"], "G1/G2 passages must differ"

        contents = [les.content_json or {} for les in session.query(LearningLesson).all()]
        dups = audit_duplicates(contents)
        if dups:
            raise RuntimeError(f"Duplicate prompts: {len(dups)}")
        session.commit()
        print(f"TV G1/G2 passages: refreshed {n} lessons")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    pass

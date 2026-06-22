"""Thêm đoạn văn đọc hiểu vào bài Tiếng Việt

Revision ID: 025_reading_passages
Revises: 024_online_teacher_steps
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "025_reading_passages"
down_revision: Union[str, None] = "024_online_teacher_steps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content
        from app.data.learning_ket_noi_content import build_lesson_content
        from app.models.learning import LearningChapter, LearningLesson, LearningSubject

        n = refresh_all_lesson_content(session)
        sample = (
            session.query(LearningLesson)
            .join(LearningChapter, LearningLesson.chapter_id == LearningChapter.id)
            .join(LearningSubject, LearningChapter.subject_id == LearningSubject.id)
            .filter(LearningSubject.id == "tieng-viet-g2", LearningLesson.sort_index == 0)
            .first()
        )
        if sample:
            passage = (sample.content_json or {}).get("passage") or []
            if len(passage) < 3:
                raise RuntimeError(f"TV lesson missing passage: {len(passage)} sentences")
        # sanity: builder trực tiếp
        direct = build_lesson_content(2, "tieng-viet", "G2-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
        if len(direct.get("passage") or []) < 3:
            raise RuntimeError("Em đến trường passage too short")
        session.commit()
        print(f"Reading passages: refreshed {n} lessons")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    pass

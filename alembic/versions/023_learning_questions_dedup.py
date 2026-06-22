"""Dedup lesson quiz prompts — global unique allocator v3

Revision ID: 023_learning_questions_dedup
Revises: 022_learning_questions_v2
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "023_learning_questions_dedup"
down_revision: Union[str, None] = "022_learning_questions_v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content
        from app.data.learning_question_allocator import audit_duplicates
        from app.models.learning import LearningLesson

        n = refresh_all_lesson_content(session)
        contents = [les.content_json or {} for les in session.query(LearningLesson).all()]
        dups = audit_duplicates(contents)
        if dups:
            raise RuntimeError(f"Duplicate prompts after refresh: {len(dups)} — e.g. {dups[0]}")
        session.commit()
        print(f"Learning questions dedup v3: refreshed {n} lessons, 0 duplicate prompts")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    pass

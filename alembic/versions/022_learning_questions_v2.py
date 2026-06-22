"""Refresh lesson quiz content — knowledge-based questions v2

Revision ID: 022_learning_questions_v2
Revises: 021_seed_ket_noi_g15
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "022_learning_questions_v2"
down_revision: Union[str, None] = "021_seed_ket_noi_g15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content

        n = refresh_all_lesson_content(session)
        session.commit()
        print(f"Learning questions v2: refreshed {n} lessons")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    pass

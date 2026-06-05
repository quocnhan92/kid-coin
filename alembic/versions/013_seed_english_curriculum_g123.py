"""Nạp chương trình Tiếng Anh lớp 1–3 (phong phú từ vựng) cho English Shooter

Revision ID: 013
Revises: 012
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.english_curriculum_g123 import seed_english_curriculum_g123
        from app.services.english_catalog_seed import ensure_english_base_catalog

        ensure_english_base_catalog(session)
        count = seed_english_curriculum_g123(session)
        session.commit()
        print(f"English Shooter G1–G3: seeded {count} themes")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.english_curriculum_g123 import delete_grades_1_2_3

        delete_grades_1_2_3(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

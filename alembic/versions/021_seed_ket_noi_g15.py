"""Seed SGK Kết nối tri thức — lộ trình học lớp 1→5

Revision ID: 021_seed_ket_noi_g15
Revises: 020_summer_learning
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

revision: str = "021_seed_ket_noi_g15"
down_revision: Union[str, None] = "020_summer_learning"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import seed_ket_noi_curriculum

        stats = seed_ket_noi_curriculum(session)
        session.commit()
        print(
            f"Learning Kết nối tri thức G1–G5: "
            f"{stats['subjects']} môn, {stats['chapters']} chủ đề, {stats['lessons']} bài"
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.data.learning_ket_noi_curriculum import delete_ket_noi_curriculum

        delete_ket_noi_curriculum(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

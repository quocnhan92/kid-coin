import logging
import os

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_alembic_upgrade() -> None:
    """
    Chạy alembic upgrade head.
    Raise exception nếu thất bại để dừng service startup.
    """
    # Resolve alembic.ini relative to project root (two levels up from this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_ini_path = os.path.join(base_dir, "alembic.ini")

    logger.info("Starting database migration: alembic upgrade head")
    try:
        cfg = Config(alembic_ini_path)
        # Override sqlalchemy.url with environment variable if set
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            cfg.set_main_option("sqlalchemy.url", database_url)

        command.upgrade(cfg, "head")
        logger.info("Database migration completed successfully.")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise

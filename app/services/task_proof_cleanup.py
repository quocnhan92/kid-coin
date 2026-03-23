from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import logging
import threading

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.logs_transactions import TaskLog, TaskStatus


logger = logging.getLogger(__name__)

# Project root: .../kid-coin
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = (PROJECT_ROOT / "app" / "static").resolve()


def _resolve_local_proof_path(proof_image_url: str) -> Optional[Path]:
    """
    Resolve proof URL to a local file path in app/static if possible.
    Supported examples:
    - /static/uploads/abc.jpg
    - https://host/static/uploads/abc.jpg
    - static/uploads/abc.jpg
    - app/static/uploads/abc.jpg
    """
    if not proof_image_url:
        return None

    if proof_image_url.startswith("data:"):
        # Embedded/base64 image, not a filesystem file.
        return None

    parsed = urlparse(proof_image_url)
    raw_path = parsed.path or proof_image_url

    if raw_path.startswith("/static/"):
        relative = raw_path[len("/static/") :]
    elif raw_path.startswith("static/"):
        relative = raw_path[len("static/") :]
    elif raw_path.startswith("app/static/"):
        relative = raw_path[len("app/static/") :]
    else:
        return None

    candidate = (STATIC_ROOT / relative).resolve()
    # Safety: only allow deletion inside app/static
    if not str(candidate).startswith(str(STATIC_ROOT)):
        return None
    return candidate


def cleanup_approved_task_proofs_older_than_five_days(db: Session) -> Tuple[int, int, int]:
    """
    Returns tuple:
    (deleted_local_files, cleared_db_references, skipped_remote_urls)
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=5)
    logs = (
        db.query(TaskLog)
        .filter(
            TaskLog.status == TaskStatus.APPROVED,
            TaskLog.resolved_at.isnot(None),
            TaskLog.resolved_at <= cutoff,
            TaskLog.proof_image_url.isnot(None),
        )
        .all()
    )

    deleted_files = 0
    cleared_references = 0
    skipped_remote = 0

    for log in logs:
        proof_url = log.proof_image_url or ""
        local_path = _resolve_local_proof_path(proof_url)

        if proof_url.startswith("data:"):
            # Embedded proof data is not a file; still clear after retention period.
            log.proof_image_url = None
            cleared_references += 1
            continue

        if local_path is None:
            skipped_remote += 1
            continue

        if local_path.exists() and local_path.is_file():
            try:
                local_path.unlink()
                deleted_files += 1
            except Exception as exc:
                logger.warning("Failed to delete proof file '%s': %s", local_path, exc)
                # Keep DB reference if delete failed.
                continue

        # File deleted or already missing; clear stale DB reference.
        log.proof_image_url = None
        cleared_references += 1

    if logs:
        db.commit()

    return deleted_files, cleared_references, skipped_remote


def run_daily_cleanup_job():
    db = SessionLocal()
    try:
        deleted_files, cleared_refs, skipped_remote = cleanup_approved_task_proofs_older_than_five_days(db)
        logger.info(
            "Daily task proof cleanup done: deleted_files=%s, cleared_refs=%s, skipped_remote=%s",
            deleted_files,
            cleared_refs,
            skipped_remote,
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Daily task proof cleanup failed: %s", exc)
    finally:
        db.close()


def _seconds_until_next_1am() -> float:
    now = datetime.now()
    next_run = now.replace(hour=1, minute=0, second=0, microsecond=0)
    if next_run <= now:
        next_run = next_run + timedelta(days=1)
    return (next_run - now).total_seconds()


def scheduler_loop(stop_event: threading.Event):
    while not stop_event.is_set():
        wait_seconds = max(1.0, _seconds_until_next_1am())
        if stop_event.wait(wait_seconds):
            break
        run_daily_cleanup_job()


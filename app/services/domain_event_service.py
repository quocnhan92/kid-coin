import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.platform import DomainEventOutbox

logger = logging.getLogger(__name__)

EVENT_TASK_APPROVED = "task.approved"
EVENT_REWARD_REDEEMED = "reward.redeemed"
EVENT_PLAY_SESSION_COMPLETED = "play.session.completed"
EVENT_USER_LEVEL_UP = "user.level_up"


def emit(
    db: Session,
    event_type: str,
    payload: Dict[str, Any],
    *,
    family_id: Optional[UUID] = None,
    aggregate_type: Optional[str] = None,
    aggregate_id: Optional[str] = None,
) -> DomainEventOutbox:
    row = DomainEventOutbox(
        event_type=event_type,
        payload_json=payload,
        family_id=family_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        status="pending",
    )
    db.add(row)
    return row


def process_pending(db: Session, limit: int = 100) -> int:
    rows: List[DomainEventOutbox] = (
        db.query(DomainEventOutbox)
        .filter(DomainEventOutbox.status == "pending")
        .order_by(DomainEventOutbox.id.asc())
        .limit(limit)
        .all()
    )
    now = datetime.now(timezone.utc)
    for row in rows:
        try:
            _dispatch(row)
            row.status = "published"
            row.published_at = now
        except Exception as exc:
            row.retry_count = int(row.retry_count or 0) + 1
            if row.retry_count >= 5:
                row.status = "failed"
            logger.warning("Outbox dispatch failed id=%s: %s", row.id, exc)
    if rows:
        db.commit()
    return len(rows)


def _dispatch(row: DomainEventOutbox) -> None:
    logger.debug("Outbox event %s type=%s", row.id, row.event_type)

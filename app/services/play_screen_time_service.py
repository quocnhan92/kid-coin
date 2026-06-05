"""Daily screen-time cap for play sessions."""
from datetime import date, datetime, timezone
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.play.policy import PlayDailyScreenTime


def _today() -> date:
    return datetime.now(timezone.utc).date()


def get_status(db: Session, user_id: UUID) -> Dict[str, Any]:
    cap = settings.PLAY_DAILY_SCREEN_MINUTES
    row = (
        db.query(PlayDailyScreenTime)
        .filter(PlayDailyScreenTime.user_id == user_id, PlayDailyScreenTime.usage_date == _today())
        .first()
    )
    used = int(row.minutes_used if row else 0)
    return {
        "cap_minutes": cap,
        "minutes_used": used,
        "minutes_remaining": max(0, cap - used),
        "blocked": used >= cap,
    }


def assert_can_play(db: Session, user_id: UUID) -> None:
    from fastapi import HTTPException

    st = get_status(db, user_id)
    if st["blocked"]:
        raise HTTPException(
            status_code=429,
            detail=f"Daily screen limit reached ({st['cap_minutes']} min)",
        )


def add_minutes(db: Session, user_id: UUID, seconds: int) -> None:
    if seconds <= 0:
        return
    mins = max(1, seconds // 60)
    today = _today()
    row = (
        db.query(PlayDailyScreenTime)
        .filter(PlayDailyScreenTime.user_id == user_id, PlayDailyScreenTime.usage_date == today)
        .first()
    )
    if not row:
        row = PlayDailyScreenTime(user_id=user_id, usage_date=today, minutes_used=0)
        db.add(row)
    row.minutes_used = int(row.minutes_used or 0) + mins
    row.updated_at = datetime.now(timezone.utc)

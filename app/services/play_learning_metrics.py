"""Shared learning progress metrics (English + Math)."""
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.play_constants import GAME_MATH_EN, GAME_MATH_VN
from app.models.play import PlaySession, PlaySessionSummary, PlayUserGameStats
from app.services.english_shooter_progress_service import merge_extra


def english_extra(db: Session, user_id: UUID) -> Dict[str, Any]:
    rows = (
        db.query(PlayUserGameStats)
        .filter(
            PlayUserGameStats.user_id == user_id,
            PlayUserGameStats.game_id == "english_shooter",
        )
        .all()
    )
    if not rows:
        return merge_extra(None)
    merged = merge_extra(None)
    max_correct = 0
    themes: set[str] = set()
    for row in rows:
        ex = merge_extra(row.extra_json)
        max_correct = max(max_correct, int(ex.get("lifetime_correct") or 0))
        themes.update(ex.get("themes_completed") or [])
    merged["lifetime_correct"] = max_correct
    merged["themes_completed"] = list(themes)
    return merged


def math_metrics_for_game(db: Session, user_id: UUID, game_id: str) -> Dict[str, int]:
    total_correct = (
        db.query(func.coalesce(func.sum(PlayUserGameStats.total_correct), 0))
        .filter(
            PlayUserGameStats.user_id == user_id,
            PlayUserGameStats.game_id == game_id,
        )
        .scalar()
        or 0
    )
    stars3 = (
        db.query(func.count(PlaySessionSummary.session_id))
        .join(PlaySession, PlaySession.id == PlaySessionSummary.session_id)
        .filter(
            PlaySession.user_id == user_id,
            PlaySession.game_id == game_id,
            PlaySessionSummary.stars_earned >= 3,
        )
        .scalar()
        or 0
    )
    return {"correct": int(total_correct), "sessions_3star": int(stars3)}


def math_metrics(db: Session, user_id: UUID) -> Dict[str, int]:
    vn = math_metrics_for_game(db, user_id, GAME_MATH_VN)
    en = math_metrics_for_game(db, user_id, GAME_MATH_EN)
    return {
        "math_vn_correct": vn["correct"],
        "math_en_correct": en["correct"],
        "math_correct": vn["correct"] + en["correct"],
        "math_sessions_3star": vn["sessions_3star"] + en["sessions_3star"],
    }

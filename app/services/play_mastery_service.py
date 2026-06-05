"""Mastery-based KPIs for reward unlock (thay total_learning_correct)."""
from decimal import Decimal
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.play import PlayLevelProgress, PlaySkillMasteryAgg, PlaySession, PlaySessionSummary
from app.services.play_learning_metrics import english_extra, math_metrics

MASTERY_THRESHOLD = Decimal("0.70")


def mastery_metrics(db: Session, user_id: UUID) -> Dict[str, Any]:
    en = english_extra(db, user_id)
    math = math_metrics(db, user_id)
    themes_done = len(en.get("themes_completed") or [])

    mastered_skills = (
        db.query(func.count(PlaySkillMasteryAgg.skill_unit_id))
        .filter(
            PlaySkillMasteryAgg.user_id == user_id,
            PlaySkillMasteryAgg.mastery_score >= MASTERY_THRESHOLD,
        )
        .scalar()
        or 0
    )
    avg_mastery = (
        db.query(func.avg(PlaySkillMasteryAgg.mastery_score))
        .filter(PlaySkillMasteryAgg.user_id == user_id)
        .scalar()
    )
    levels_3star = (
        db.query(func.count(PlayLevelProgress.level_id))
        .filter(
            PlayLevelProgress.user_id == user_id,
            PlayLevelProgress.stars >= 3,
        )
        .scalar()
        or 0
    )
    math_3star_sessions = math["math_sessions_3star"]

    return {
        "skills_mastered_count": int(mastered_skills),
        "avg_mastery_score": float(avg_mastery or 0),
        "english_themes_done": themes_done,
        "math_levels_3star": int(levels_3star),
        "math_sessions_3star": int(math_3star_sessions),
        "english_themes_mastered": themes_done,
    }

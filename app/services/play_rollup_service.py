"""Rollup level progress, mastery, and stats after session end."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.play import (
    PlayLevel,
    PlayLevelProgress,
    PlaySkillMasteryAgg,
    PlayUserGameStats,
    PlayModeProgress,
    PlayEvent,
)
from app.schemas.play import SessionSummaryIn


def _unlock_next_levels(db: Session, user_id: UUID, level_id: str) -> List[str]:
    unlocked: List[str] = []
    next_levels = [
        nl
        for nl in db.query(PlayLevel).all()
        if level_id in (nl.prerequisite_level_ids or [])
    ]
    for nl in next_levels:
        prog = db.query(PlayLevelProgress).filter(
            PlayLevelProgress.user_id == user_id,
            PlayLevelProgress.level_id == nl.id,
        ).first()
        if not prog:
            prog = PlayLevelProgress(
                user_id=user_id,
                level_id=nl.id,
                is_unlocked=True,
                stars=0,
            )
            db.add(prog)
        elif not prog.is_unlocked:
            prog.is_unlocked = True
        unlocked.append(nl.id)
    return unlocked


def ensure_initial_level_unlock(db: Session, user_id: UUID, game_mode_id: str) -> None:
    first = (
        db.query(PlayLevel)
        .filter(PlayLevel.game_mode_id == game_mode_id)
        .order_by(PlayLevel.sort_index)
        .first()
    )
    if not first:
        return
    prog = db.query(PlayLevelProgress).filter(
        PlayLevelProgress.user_id == user_id,
        PlayLevelProgress.level_id == first.id,
    ).first()
    if not prog:
        db.add(
            PlayLevelProgress(
                user_id=user_id,
                level_id=first.id,
                stars=0,
                is_unlocked=True,
                attempts=0,
            )
        )


def rollup_after_session_end(
    db: Session,
    user_id: UUID,
    game_id: str,
    game_mode_id: Optional[str],
    summary: SessionSummaryIn,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    result: Dict[str, Any] = {
        "level_progress": None,
        "mastery_updated": [],
        "new_high_score": False,
    }

    mode_key = game_mode_id or ""
    stats = db.query(PlayUserGameStats).filter(
        PlayUserGameStats.user_id == user_id,
        PlayUserGameStats.game_id == game_id,
        PlayUserGameStats.game_mode_id == mode_key,
    ).first()
    if not stats:
        stats = PlayUserGameStats(
            user_id=user_id,
            game_id=game_id,
            game_mode_id=mode_key,
            high_score=0,
            total_sessions=0,
            total_play_time_s=0,
            total_questions=0,
            total_correct=0,
            extra_json={},
        )
        db.add(stats)

    stats.total_sessions = (stats.total_sessions or 0) + 1
    stats.total_play_time_s = (stats.total_play_time_s or 0) + int(summary.duration_s)
    stats.total_questions = (stats.total_questions or 0) + summary.questions_count
    stats.total_correct = (stats.total_correct or 0) + summary.correct_count

    if summary.score is not None and summary.score > (stats.high_score or 0):
        stats.high_score = summary.score
        stats.high_score_at = now
        result["new_high_score"] = True

    if game_mode_id == "math_blast:candy" and summary.level_id:
        ensure_initial_level_unlock(db, user_id, game_mode_id)
        prog = db.query(PlayLevelProgress).filter(
            PlayLevelProgress.user_id == user_id,
            PlayLevelProgress.level_id == summary.level_id,
        ).first()
        if not prog:
            prog = PlayLevelProgress(
                user_id=user_id,
                level_id=summary.level_id,
                stars=0,
                is_unlocked=True,
            )
            db.add(prog)

        prog.attempts = (prog.attempts or 0) + 1
        prog.last_played_at = now
        if summary.stars is not None and summary.stars > prog.stars:
            prog.stars = summary.stars
        if summary.accuracy is not None:
            acc = Decimal(str(round(summary.accuracy, 4)))
            if prog.best_accuracy is None or acc > prog.best_accuracy:
                prog.best_accuracy = acc
        if summary.stars and summary.stars >= 1 and prog.first_cleared_at is None:
            prog.first_cleared_at = now

        unlocked_next = _unlock_next_levels(db, user_id, summary.level_id)
        result["level_progress"] = {
            "level_id": summary.level_id,
            "stars": prog.stars,
            "unlocked_next": unlocked_next,
        }

        events = (
            db.query(PlayEvent)
            .filter(
                PlayEvent.user_id == user_id,
                PlayEvent.level_id == summary.level_id,
                PlayEvent.correct.isnot(None),
            )
            .order_by(PlayEvent.occurred_at.desc())
            .limit(50)
            .all()
        )
        if events:
            correct = sum(1 for e in events if e.correct)
            acc = correct / len(events)
            skill_id = events[0].skill_unit_id or "l1_add_within_10"
            mastery = db.query(PlaySkillMasteryAgg).filter(
                PlaySkillMasteryAgg.user_id == user_id,
                PlaySkillMasteryAgg.skill_unit_id == skill_id,
            ).first()
            if not mastery:
                mastery = PlaySkillMasteryAgg(user_id=user_id, skill_unit_id=skill_id)
                db.add(mastery)
            mastery.rolling_accuracy = Decimal(str(round(acc, 4)))
            mastery.mastery_score = Decimal(str(round(min(1.0, acc * 0.9 + 0.1), 4)))
            mastery.practice_count = (mastery.practice_count or 0) + summary.questions_count
            mastery.last_practiced_at = now
            latencies = [e.latency_ms for e in events if e.correct and e.latency_ms]
            if latencies:
                mastery.rolling_avg_latency_ms = int(sum(latencies) / len(latencies))
            result["mastery_updated"].append(skill_id)

    if game_mode_id == "math_blast:flappy" and summary.score is not None:
        extra = stats.extra_json or {}
        tier = (summary.summary_json or {}).get("tier", "T1")
        pb = extra.get("personal_best_by_tier", {})
        if summary.score > pb.get(tier, 0):
            pb[tier] = summary.score
            extra["personal_best_by_tier"] = pb
            stats.extra_json = extra
        tier_prog = db.query(PlayModeProgress).filter(
            PlayModeProgress.user_id == user_id,
            PlayModeProgress.game_mode_id == "math_blast:flappy",
            PlayModeProgress.tier_key == tier,
        ).first()
        if not tier_prog:
            tier_prog = PlayModeProgress(
                user_id=user_id,
                game_mode_id="math_blast:flappy",
                tier_key=tier,
                mastery_status="in_progress",
                unlocked_at=now,
            )
            db.add(tier_prog)

    db.flush()
    return result

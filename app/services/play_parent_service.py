"""Parent read paths for Play Hub."""
import hashlib
from datetime import date, datetime, timedelta, timezone
from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.gamification import UserStreak
from app.models.play import (
    PlayProfile,
    PlaySession,
    PlaySessionSummary,
    PlayLevelProgress,
    PlaySkillMasteryAgg,
    PlaySkillUnit,
    PlayUserGameStats,
    PlayLevel,
    PlayDailyRecommendation,
)
from app.models.user_family import User, Role
from app.schemas.play import (
    ParentDashboardResponse,
    ParentChildDashboard,
    ParentChildGameSummary,
    PlayRecommendationOut,
    ParentChildLevelsResponse,
    PlayLevelProgressOut,
)


def _period_start(period: str) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "30d":
        return now - timedelta(days=30)
    if period == "week":
        return now - timedelta(days=7)
    return now - timedelta(days=7)


def get_parent_dashboard(db: Session, parent: User, period: str) -> ParentDashboardResponse:
    since = _period_start(period)
    kids = (
        db.query(User)
        .filter(User.family_id == parent.family_id, User.role == Role.KID, User.is_deleted == False)
        .all()
    )
    children: List[ParentChildDashboard] = []

    for kid in kids:
        profile = db.query(PlayProfile).filter(PlayProfile.user_id == kid.id).first()
        sessions_q = db.query(PlaySession).filter(
            PlaySession.user_id == kid.id,
            PlaySession.started_at >= since,
        )
        total_sessions = sessions_q.count()
        learning_sessions = sessions_q.filter(
            PlaySession.game_mode_id.in_(["math_blast:candy", "math_blast:flappy"])
        ).count()

        play_time = (
            db.query(func.coalesce(func.sum(PlaySessionSummary.duration_s), 0))
            .join(PlaySession, PlaySession.id == PlaySessionSummary.session_id)
            .filter(PlaySession.user_id == kid.id, PlaySession.started_at >= since)
            .scalar()
        )

        streak = db.query(UserStreak).filter(UserStreak.user_id == kid.id).first()
        by_game: List[ParentChildGameSummary] = []

        candy_cleared = (
            db.query(func.count(PlayLevelProgress.level_id))
            .join(PlayLevel, PlayLevel.id == PlayLevelProgress.level_id)
            .filter(
                PlayLevelProgress.user_id == kid.id,
                PlayLevel.game_mode_id == "math_blast:candy",
                PlayLevelProgress.stars >= 1,
            )
            .scalar()
        )
        candy_sessions = sessions_q.filter(PlaySession.game_mode_id == "math_blast:candy").count()
        weak = (
            db.query(PlaySkillMasteryAgg, PlaySkillUnit)
            .join(PlaySkillUnit, PlaySkillUnit.id == PlaySkillMasteryAgg.skill_unit_id)
            .filter(PlaySkillMasteryAgg.user_id == kid.id)
            .order_by(PlaySkillMasteryAgg.mastery_score)
            .limit(3)
            .all()
        )
        recent = (
            db.query(PlayLevelProgress, PlayLevel)
            .join(PlayLevel, PlayLevel.id == PlayLevelProgress.level_id)
            .filter(
                PlayLevelProgress.user_id == kid.id,
                PlayLevel.game_mode_id == "math_blast:candy",
                PlayLevelProgress.last_played_at.isnot(None),
            )
            .order_by(PlayLevelProgress.last_played_at.desc())
            .limit(5)
            .all()
        )
        by_game.append(
            ParentChildGameSummary(
                game_id="math_blast",
                game_mode_id="math_blast:candy",
                sessions=candy_sessions,
                levels_cleared=candy_cleared or 0,
                avg_accuracy=float(weak[0][0].rolling_accuracy) if weak else None,
                weak_skills=[
                    {
                        "skill_unit_id": m.skill_unit_id,
                        "mastery_score": float(m.mastery_score),
                        "title": u.title,
                    }
                    for m, u in weak[:2]
                ],
                recent_levels=[
                    {
                        "level_id": lv.id,
                        "title": lv.title,
                        "stars": prog.stars,
                        "played_at": prog.last_played_at.isoformat() if prog.last_played_at else None,
                    }
                    for prog, lv in recent
                ],
            )
        )

        flappy_stats = db.query(PlayUserGameStats).filter(
            PlayUserGameStats.user_id == kid.id,
            PlayUserGameStats.game_id == "math_blast",
            PlayUserGameStats.game_mode_id == "math_blast:flappy",
        ).first()
        flappy_sessions = sessions_q.filter(PlaySession.game_mode_id == "math_blast:flappy").count()
        pb = 0
        if flappy_stats and flappy_stats.extra_json:
            pb = max(flappy_stats.extra_json.get("personal_best_by_tier", {}).values() or [0])
        elif flappy_stats:
            pb = int(flappy_stats.high_score)
        by_game.append(
            ParentChildGameSummary(
                game_id="math_blast",
                game_mode_id="math_blast:flappy",
                sessions=flappy_sessions,
                personal_best=pb,
                daily_session_count=flappy_sessions,
                soft_cap=profile.parental_soft_cap_sessions_day if profile else 6,
            )
        )

        today_rec = []
        rec = (
            db.query(PlayDailyRecommendation)
            .filter(
                PlayDailyRecommendation.user_id == kid.id,
                PlayDailyRecommendation.recommendation_date == date.today(),
            )
            .first()
        )
        if rec and rec.items_json:
            today_rec = [PlayRecommendationOut(**i) for i in rec.items_json]

        children.append(
            ParentChildDashboard(
                user_id=kid.id,
                display_name=kid.display_name,
                target_grade=profile.target_grade if profile else None,
                streak={"current": streak.current_streak if streak else 0},
                totals={
                    "sessions": total_sessions,
                    "play_time_minutes": int(float(play_time) / 60),
                    "learning_sessions": learning_sessions,
                },
                by_game=by_game,
                recommendations_today=today_rec,
            )
        )

    etag_src = f"{parent.family_id}:{period}:{len(children)}"
    digest = hashlib.md5(etag_src.encode()).hexdigest()[:12]
    return ParentDashboardResponse(
        family_id=parent.family_id,
        period=period,
        children=children,
        etag=f'W/"parent-{digest}"',
    )


def get_child_levels(db: Session, parent: User, child_id: UUID) -> ParentChildLevelsResponse:
    child = db.query(User).filter(User.id == child_id).first()
    if not child or child.family_id != parent.family_id or child.role != Role.KID:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Child not found in family")

    rows = (
        db.query(PlayLevelProgress)
        .filter(PlayLevelProgress.user_id == child_id, PlayLevelProgress.is_unlocked == True)
        .all()
    )
    return ParentChildLevelsResponse(
        user_id=child_id,
        levels=[
            PlayLevelProgressOut(
                level_id=p.level_id,
                stars=p.stars,
                is_unlocked=p.is_unlocked,
                last_played_at=p.last_played_at,
            )
            for p in rows
        ],
    )

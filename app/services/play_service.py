"""Play Hub read paths: bootstrap, games catalog, history, leaderboard."""
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.gamification import UserStreak
from app.models.play import (
    PlayGame,
    PlayGameMode,
    PlayContentPack,
    PlayProfile,
    PlayLevelProgress,
    PlaySkillMasteryAgg,
    PlayUserGameStats,
    PlayModeProgress,
    PlaySession,
    PlaySessionSummary,
    PlayDailyRecommendation,
    PlayLevel,
)
from app.models.user_family import User, Role
from app.schemas.play import (
    PlayBootstrapResponse,
    PlayLevelsResponse,
    PlayLevelCatalogItem,
    PlayProfileOut,
    PlayContentPackOut,
    PlayMasteryOut,
    PlayLevelProgressOut,
    PlayRecommendationOut,
    PlayGameStatsOut,
    PlayFlappyBootstrapOut,
    PlayStreakOut,
    PlayGamesResponse,
    PlayGameCatalogItem,
    PlayModeCatalogItem,
    PlayHistoryResponse,
    PlayHistoryItem,
    LeaderboardResponse,
    LeaderboardEntry,
)
from app.services.play_rollup_service import ensure_initial_level_unlock


def get_or_create_profile(db: Session, user: User) -> PlayProfile:
    profile = db.query(PlayProfile).filter(PlayProfile.user_id == user.id).first()
    if profile:
        return profile
    birth_year = user.birth_date.year if user.birth_date else None
    profile = PlayProfile(
        user_id=user.id,
        family_id=user.family_id,
        birth_year=birth_year,
        target_grade=2,
        preferences_json={
            "tts": True,
            "modes_enabled": ["candy", "flappy", "arcade_free"],
        },
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def compute_bootstrap_etag(db: Session, user_id: UUID, game_id: str, mode_id: Optional[str]) -> str:
    profile = db.query(PlayProfile).filter(PlayProfile.user_id == user_id).first()
    updated = profile.updated_at.isoformat() if profile and profile.updated_at else ""
    lp_count = db.query(func.count(PlayLevelProgress.level_id)).filter(
        PlayLevelProgress.user_id == user_id
    ).scalar()
    payload = f"{user_id}:{game_id}:{mode_id}:{updated}:{lp_count}"
    digest = hashlib.md5(payload.encode()).hexdigest()[:16]
    return f'W/"{digest}"'


def list_levels(db: Session, game_mode_id: str) -> PlayLevelsResponse:
    rows = (
        db.query(PlayLevel)
        .filter(PlayLevel.game_mode_id == game_mode_id)
        .order_by(PlayLevel.sort_index)
        .all()
    )
    return PlayLevelsResponse(
        game_mode_id=game_mode_id,
        levels=[
            PlayLevelCatalogItem(
                id=lv.id,
                title=lv.title,
                chapter_id=lv.chapter_id,
                is_boss=lv.is_boss,
                prerequisite_level_ids=lv.prerequisite_level_ids or [],
                sort_index=lv.sort_index,
                objective=lv.objective,
            )
            for lv in rows
        ],
    )


def list_games(db: Session) -> PlayGamesResponse:
    games = db.query(PlayGame).filter(PlayGame.is_active == True).order_by(PlayGame.sort_order).all()
    out: List[PlayGameCatalogItem] = []
    for g in games:
        modes = (
            db.query(PlayGameMode)
            .filter(PlayGameMode.game_id == g.id)
            .all()
        )
        out.append(
            PlayGameCatalogItem(
                id=g.id,
                display_name=g.display_name,
                game_type=g.game_type,
                meta=g.meta_json or {},
                modes=[
                    PlayModeCatalogItem(
                        id=m.id,
                        display_name=m.display_name,
                        tracks_learning=m.tracks_learning,
                    )
                    for m in modes
                ],
            )
        )
    return PlayGamesResponse(games=out)


def get_bootstrap(
    db: Session,
    user: User,
    game_id: str,
    game_mode_id: Optional[str],
) -> Tuple[PlayBootstrapResponse, str]:
    profile = get_or_create_profile(db, user)
    prefs = profile.preferences_json or {}

    pack_out = None
    if game_mode_id and "candy" in game_mode_id:
        pack = db.query(PlayContentPack).filter(
            PlayContentPack.id == profile.active_content_pack_id
        ).first()
        if pack:
            pack_out = PlayContentPackOut(
                id=pack.id,
                manifest_version=pack.manifest_version,
                manifest_hash=pack.manifest_hash,
                manifest_url=f"/static/manifests/{pack.id}.json",
            )
        ensure_initial_level_unlock(db, user.id, game_mode_id)
        db.commit()

    mastery_rows = db.query(PlaySkillMasteryAgg).filter(PlaySkillMasteryAgg.user_id == user.id).all()
    mastery = [
        PlayMasteryOut(
            skill_unit_id=m.skill_unit_id,
            mastery_score=float(m.mastery_score),
            rolling_accuracy=float(m.rolling_accuracy),
        )
        for m in mastery_rows
    ]

    lp_query = db.query(PlayLevelProgress).filter(PlayLevelProgress.user_id == user.id)
    if game_mode_id:
        level_ids = [
            row[0]
            for row in db.query(PlayLevel.id).filter(PlayLevel.game_mode_id == game_mode_id).all()
        ]
        if level_ids:
            lp_query = lp_query.filter(PlayLevelProgress.level_id.in_(level_ids))
    level_progress = [
        PlayLevelProgressOut(
            level_id=p.level_id,
            stars=p.stars,
            is_unlocked=p.is_unlocked,
            last_played_at=p.last_played_at,
        )
        for p in lp_query.all()
    ]

    today = date.today()
    rec_row = (
        db.query(PlayDailyRecommendation)
        .filter(
            PlayDailyRecommendation.user_id == user.id,
            PlayDailyRecommendation.recommendation_date == today,
        )
        .first()
    )
    recommendations = []
    if rec_row and rec_row.items_json:
        for item in rec_row.items_json:
            recommendations.append(PlayRecommendationOut(**item))
    elif mastery_rows:
        weakest = min(mastery_rows, key=lambda m: float(m.mastery_score))
        recommendations.append(
            PlayRecommendationOut(
                type="review",
                skill_unit_id=weakest.skill_unit_id,
                reason="low_mastery",
                label="Ôn kỹ năng cần củng cố",
            )
        )

    mode_key = game_mode_id or ""
    stats = db.query(PlayUserGameStats).filter(
        PlayUserGameStats.user_id == user.id,
        PlayUserGameStats.game_id == game_id,
        PlayUserGameStats.game_mode_id == mode_key,
    ).first()
    game_stats = PlayGameStatsOut(
        high_score=int(stats.high_score) if stats else 0,
        total_sessions=stats.total_sessions if stats else 0,
    )

    flappy_out = None
    if game_mode_id == "math_blast:flappy":
        tiers = db.query(PlayModeProgress).filter(
            PlayModeProgress.user_id == user.id,
            PlayModeProgress.game_mode_id == "math_blast:flappy",
        ).all()
        extra = (stats.extra_json if stats else {}) or {}
        pb = extra.get("personal_best_by_tier", {})
        flappy_out = PlayFlappyBootstrapOut(
            tier_unlocked=[t.tier_key for t in tiers if t.mastery_status != "locked"] or ["T1"],
            tier_mastery_progress={
                t.tier_key: str(t.mastery_window_json.get("label", "0/20"))
                for t in tiers
            },
            personal_best=pb,
            daily_session_count=_daily_session_count(db, user.id, "math_blast:flappy"),
            daily_session_soft_cap=profile.parental_soft_cap_sessions_day,
        )

    streak_row = db.query(UserStreak).filter(UserStreak.user_id == user.id).first()
    streak = PlayStreakOut(
        current=streak_row.current_streak if streak_row else 0,
        last_active_date=streak_row.last_active_date if streak_row else None,
    )

    body = PlayBootstrapResponse(
        profile=PlayProfileOut(
            user_id=user.id,
            target_grade=profile.target_grade,
            active_content_pack_id=profile.active_content_pack_id,
            preferences=prefs,
        ),
        content_pack=pack_out,
        mastery=mastery,
        level_progress=level_progress,
        recommendations_today=recommendations,
        game_stats=game_stats,
        flappy=flappy_out,
        streak=streak,
    )
    etag = compute_bootstrap_etag(db, user.id, game_id, game_mode_id)
    return body, etag


def _daily_session_count(db: Session, user_id: UUID, game_mode_id: str) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        db.query(func.count(PlaySession.id))
        .filter(
            PlaySession.user_id == user_id,
            PlaySession.game_mode_id == game_mode_id,
            PlaySession.started_at >= start,
        )
        .scalar()
        or 0
    )


def get_history(
    db: Session,
    user_id: UUID,
    game_id: Optional[str],
    game_mode_id: Optional[str],
    limit: int,
    cursor: Optional[str],
) -> PlayHistoryResponse:
    q = (
        db.query(PlaySession, PlaySessionSummary)
        .outerjoin(PlaySessionSummary, PlaySessionSummary.session_id == PlaySession.id)
        .filter(PlaySession.user_id == user_id, PlaySession.status == "completed")
        .order_by(PlaySession.started_at.desc())
    )
    if game_id:
        q = q.filter(PlaySession.game_id == game_id)
    if game_mode_id:
        q = q.filter(PlaySession.game_mode_id == game_mode_id)
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            q = q.filter(PlaySession.started_at < cursor_dt)
        except ValueError:
            pass

    rows = q.limit(limit + 1).all()
    items: List[PlayHistoryItem] = []
    next_cursor = None
    for session, summary in rows[:limit]:
        mode_key = None
        if session.game_mode_id and ":" in session.game_mode_id:
            mode_key = session.game_mode_id.split(":", 1)[1]
        items.append(
            PlayHistoryItem(
                session_id=session.id,
                started_at=session.started_at,
                duration_s=float(summary.duration_s) if summary else 0,
                mode=mode_key,
                level_id=summary.level_id if summary else None,
                stars=summary.stars_earned if summary else None,
                accuracy=float(summary.accuracy) if summary and summary.accuracy else None,
                score=int(summary.score) if summary and summary.score else None,
            )
        )
    if len(rows) > limit:
        next_cursor = items[-1].started_at.isoformat() if items else None

    return PlayHistoryResponse(items=items, next_cursor=next_cursor)


def get_leaderboard(
    db: Session,
    user: User,
    game_id: str,
    game_mode_id: str,
    tier: Optional[str],
    period: str,
) -> LeaderboardResponse:
    since = datetime.now(timezone.utc) - timedelta(days=1 if period == "daily" else 7)
    kids = db.query(User).filter(User.family_id == user.family_id, User.role == Role.KID).all()
    entries: List[LeaderboardEntry] = []
    your_score = None
    your_rank = None

    for kid in kids:
        stats = db.query(PlayUserGameStats).filter(
            PlayUserGameStats.user_id == kid.id,
            PlayUserGameStats.game_id == game_id,
            PlayUserGameStats.game_mode_id == game_mode_id,
        ).first()
        score = 0
        if stats:
            if tier and stats.extra_json:
                score = stats.extra_json.get("personal_best_by_tier", {}).get(tier, 0)
            else:
                score = int(stats.high_score)
        recent = (
            db.query(PlaySession)
            .filter(
                PlaySession.user_id == kid.id,
                PlaySession.game_mode_id == game_mode_id,
                PlaySession.started_at >= since,
            )
            .first()
        )
        if not recent and score == 0:
            continue
        entries.append(
            LeaderboardEntry(
                rank=0,
                display_name=kid.display_name,
                score=score,
                is_you=(kid.id == user.id),
            )
        )

    entries.sort(key=lambda e: e.score, reverse=True)
    for i, e in enumerate(entries, start=1):
        e.rank = i
        if e.is_you:
            your_rank = i
            your_score = e.score

    return LeaderboardResponse(
        period=period,
        tier=tier,
        entries=entries[:10],
        your_rank=your_rank,
        your_score=your_score,
    )

"""Reward Playground — unlock fun games from learning progress."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.play_constants import REWARD_PLAY_COST
from app.data.reward_playground_catalog import (
    ALL_ROLLOUT,
    REWARD_GAME_BY_ID,
    REWARD_GAMES,
    REWARD_SECTIONS,
    RULES,
    RULE_HINTS,
    VISIBLE_ROLLOUT,
    reward_flag_key,
)
from app.services.play_engagement_service import (
    FIRST_PLAY_FREE_GAME_IDS,
    is_first_play_free_eligible,
    onboarding_payload,
)
from app.services.play_learning_metrics import english_extra, math_metrics
from app.services.play_mastery_service import mastery_metrics
from app.services.play_wallet_service import get_or_create_wallet, wallet_snapshot


def _safe_wallet(db: Session, user_id: UUID) -> Optional[Dict[str, Any]]:
    try:
        return wallet_snapshot(get_or_create_wallet(db, user_id))
    except ProgrammingError:
        db.rollback()
        return None


def learning_metrics(db: Session, user_id: UUID) -> Dict[str, Any]:
    en = english_extra(db, user_id)
    math = math_metrics(db, user_id)
    mastery = mastery_metrics(db, user_id)
    en_correct = int(en.get("lifetime_correct") or 0)
    themes_done = len(en.get("themes_completed") or [])
    math_correct = math["math_correct"]
    return {
        **mastery,
        "english_correct": en_correct,
        "english_themes_done": themes_done,
        "math_vn_correct": math["math_vn_correct"],
        "math_en_correct": math["math_en_correct"],
        "math_correct": math_correct,
        "math_sessions_3star": math["math_sessions_3star"],
        "total_learning_correct": en_correct + math_correct,
    }


def apply_test_unlock(db: Session, extra: Dict[str, Any]) -> Dict[str, Any]:
    from app.services.feature_flag_service import is_enabled

    if not is_enabled(db, "play.test_unlock_all"):
        return extra
    blocks = dict(extra.get("blocks") or {})
    blocks["city"] = {**blocks.get("city", {}), "unlocked": True}
    blocks["boss"] = {**blocks.get("boss", {}), "unlocked": True}
    extra["blocks"] = blocks
    extra["test_unlock_all"] = True
    return extra


def is_reward_game_flag_enabled(db: Session, game: Dict[str, Any]) -> bool:
    from app.models.platform import FeatureFlag
    from app.services.feature_flag_service import is_enabled

    key = reward_flag_key(game["id"])
    rows = db.query(FeatureFlag).filter(FeatureFlag.key == key).all()
    if rows:
        return is_enabled(db, key)
    status = game.get("rollout_status", "draft")
    if status == "live":
        return True
    if status == "beta":
        return settings.PLAY_TEST_UNLOCK_ALL
    return settings.PLAY_TEST_UNLOCK_ALL


def _rollout_allowed(status: str, *, test_all: bool, include_draft: bool) -> bool:
    if test_all or include_draft:
        return status in ALL_ROLLOUT
    return status in VISIBLE_ROLLOUT


def _game_unlocked(
    g: Dict[str, Any],
    *,
    test_all: bool,
    metrics: Optional[Dict[str, Any]],
) -> bool:
    if test_all:
        return True
    if not metrics:
        return False
    check = RULES.get(g["rule_key"])
    return bool(check and check(metrics))


def _build_game_item(
    g: Dict[str, Any],
    *,
    test_all: bool,
    metrics: Optional[Dict[str, Any]],
    first_play_free: bool = False,
) -> Dict[str, Any]:
    rule_key = g["rule_key"]
    unlocked = _game_unlocked(g, test_all=test_all, metrics=metrics)
    cost = REWARD_PLAY_COST.get(g["id"], 0)
    if first_play_free and g["id"] in FIRST_PLAY_FREE_GAME_IDS:
        unlocked = True
        cost = 0
    return {
        **g,
        "unlocked": unlocked,
        "unlock_hint": RULE_HINTS.get(rule_key, ""),
        "play_cost": cost,
    }


def _build_sections(visible_ids: List[str], db: Session) -> List[Dict[str, Any]]:
    from app.services.feature_flag_service import is_enabled

    visible = set(visible_ids)
    sections: List[Dict[str, Any]] = []
    for sec in REWARD_SECTIONS:
        flag = sec.get("section_flag")
        if flag and not is_enabled(db, flag):
            continue
        game_ids = [gid for gid in sec["game_ids"] if gid in visible]
        if not game_ids:
            continue
        sections.append(
            {
                "key": sec["key"],
                "title_en": sec["title_en"],
                "title_vi": sec["title_vi"],
                "game_ids": game_ids,
            }
        )
    return sections


def build_reward_playground(
    db: Session,
    user_id: Optional[UUID],
    *,
    genre: Optional[str] = None,
    include_draft: bool = False,
) -> Dict[str, Any]:
    from app.services.feature_flag_service import is_enabled

    test_all = is_enabled(db, "play.test_unlock_all")
    allow_draft = include_draft and test_all
    metrics = learning_metrics(db, user_id) if user_id else None
    first_free = is_first_play_free_eligible(db, user_id)
    wallet = _safe_wallet(db, user_id) if user_id else None
    from app.core.config import settings

    skip_spend = settings.PLAY_SKIP_REWARD_SPEND or test_all or first_free
    games: List[Dict[str, Any]] = []
    for g in REWARD_GAMES:
        if genre and g.get("genre") != genre:
            continue
        if not _rollout_allowed(
            g.get("rollout_status", "draft"),
            test_all=test_all,
            include_draft=allow_draft,
        ):
            continue
        if not is_reward_game_flag_enabled(db, g):
            continue
        games.append(
            _build_game_item(
                g, test_all=test_all, metrics=metrics, first_play_free=first_free
            )
        )
    visible_ids = [g["id"] for g in games]
    return {
        "test_unlock_all": test_all,
        "skip_reward_spend": skip_spend,
        "logged_in": user_id is not None,
        "metrics": metrics,
        "wallet": wallet,
        "games": games,
        "sections": _build_sections(visible_ids, db),
        "unlocked_count": sum(1 for x in games if x["unlocked"]),
        "total_count": len(games),
        "onboarding": onboarding_payload(db, user_id),
    }


def validate_reward_play(
    db: Session,
    user_id: UUID,
    reward_game_id: str,
) -> tuple[bool, str, int]:
    """Return ok, error message, http_status."""
    from app.services.feature_flag_service import is_enabled

    g = REWARD_GAME_BY_ID.get(reward_game_id)
    if not g:
        return False, "Unknown reward game", 400

    test_all = is_enabled(db, "play.test_unlock_all")
    status = g.get("rollout_status", "draft")
    if status == "draft" and not test_all:
        return False, "Game not available yet", 400
    if not is_reward_game_flag_enabled(db, g):
        return False, "Game not enabled", 404

    metrics = learning_metrics(db, user_id)
    if not _game_unlocked(g, test_all=test_all, metrics=metrics):
        if not (
            is_first_play_free_eligible(db, user_id)
            and reward_game_id in FIRST_PLAY_FREE_GAME_IDS
        ):
            return False, "Game locked — keep learning to unlock", 403

    cost = REWARD_PLAY_COST.get(reward_game_id)
    if cost is None:
        return False, "Unknown reward game", 400
    return True, "", cost

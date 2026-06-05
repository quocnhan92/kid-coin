import logging
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.play import PlayGame
from app.services.feature_flag_service import upsert_flag

logger = logging.getLogger(__name__)

CORE_FLAGS: Tuple[Tuple[str, bool, str], ...] = (
    ("core.auth", True, "M1 Identity & Access"),
    ("core.tasks", True, "M3 Task & Reward"),
    ("core.gamification", True, "M4 Gamification"),
    ("core.finance", True, "M5 Finance"),
    ("mod.thinking", True, "M6 Critical Thinking"),
    ("mod.social", True, "M7 Family Social"),
    ("mod.teen", True, "M8 Teen Mode"),
    ("mod.clubs", True, "M9 Clubs"),
    ("play.hub", True, "M10 Play Hub"),
    ("play.reward_playground", True, "Reward Playground"),
    ("play.test_unlock_all", settings.PLAY_TEST_UNLOCK_ALL, "Dev unlock all play gates"),
    ("play.reward.co_op_hub", settings.PLAY_TEST_UNLOCK_ALL, "Co-op section on reward page"),
    ("mod.ads", False, "M14 Ad System (beta)"),
)

HUB_ZONE_MAP: Dict[str, Tuple[str, Optional[str], bool, int, int]] = {
    "math_blast": ("learning", "math", False, 1, 5),
    "english_shooter": ("learning", "english", False, 1, 5),
    "english_math": ("learning", "math", False, 1, 5),
    "memory_learn": ("learning", "memory", False, 1, 5),
    "memory": ("reward", None, True, 1, 5),
    "snake": ("reward", None, True, 1, 5),
    "2048": ("reward", None, True, 1, 5),
    "flappy_classic": ("reward", None, True, 1, 5),
}

GAME_ROUTE_MAP: Dict[str, Tuple[str, str]] = {
    "math_blast": ("games/english_math_v2_hub.html", "/game/math-blast-v2"),
    "snake": ("games/snake.html", "/game/snake"),
    "2048": ("games/2048.html", "/game/2048"),
    "memory_learn": ("games/memory.html", "/game/memory-learn"),
    "memory": ("games/memory.html", "/game/memory"),
    "flappy_classic": ("games/flappy.html", "/game/flappy"),
    "english_shooter": ("games/english_shooter_hub.html", "/game/english-shooter"),
    "english_math": ("games/english_math_hub.html", "/game/english-shooter/math"),
}


def seed_platform(db: Session) -> None:
    for key, enabled, desc in CORE_FLAGS:
        upsert_flag(db, key, enabled, description=desc)
    _seed_reward_game_flags(db)
    sync_play_game_routes(db)
    db.commit()
    logger.info("Platform seed: feature flags + play game routes synced")


def _seed_reward_game_flags(db: Session) -> None:
    from app.data.reward_playground_catalog import REWARD_GAMES, reward_flag_key

    for g in REWARD_GAMES:
        gid = g["id"]
        status = g.get("rollout_status", "draft")
        if status == "live":
            enabled = True
        elif status == "beta":
            enabled = settings.PLAY_TEST_UNLOCK_ALL
        else:
            enabled = settings.PLAY_TEST_UNLOCK_ALL
        upsert_flag(
            db,
            reward_flag_key(gid),
            enabled,
            description=f"Reward game gate: {gid} ({status})",
        )


def sync_play_game_routes(db: Session) -> None:
    games = db.query(PlayGame).all()
    for game in games:
        zone_meta = HUB_ZONE_MAP.get(game.id)
        if zone_meta:
            hub_zone, subject, requires_wallet, gmin, gmax = zone_meta
            game.hub_zone = hub_zone
            game.subject = subject
            game.requires_wallet = requires_wallet
            game.grade_min = gmin
            game.grade_max = gmax
            if hub_zone == "reward":
                game.is_public = False
        mapped = GAME_ROUTE_MAP.get(game.id)
        if mapped:
            template, url = mapped
            if not game.ssr_template:
                game.ssr_template = template
            if not game.launch_url:
                game.launch_url = url
        elif game.meta_json and isinstance(game.meta_json, dict):
            route = game.meta_json.get("route")
            if route and not game.launch_url:
                game.launch_url = route


def game_launch_meta(game: PlayGame) -> Dict[str, Optional[str]]:
    url = game.launch_url or (game.meta_json or {}).get("route")
    return {
        "launch_url": url,
        "ssr_template": game.ssr_template,
        "is_public": bool(game.is_public),
        "min_client_version": game.min_client_version or "1.0.0",
    }

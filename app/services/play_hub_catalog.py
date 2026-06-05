"""Play Hub catalog — learning vs reward zones (blueprint play-hub-game-taxonomy)."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.play import PlayGame
from app.schemas.platform import PublicGameItem
from app.services.feature_flag_service import is_enabled
from app.services.platform_seed import game_launch_meta

ZONE_LEARNING = "learning"
ZONE_REWARD = "reward"


def list_hub_games(
    db: Session,
    *,
    zone: str = ZONE_LEARNING,
    grade: Optional[int] = None,
    market: Optional[str] = None,
) -> List[PublicGameItem]:
    q = db.query(PlayGame).filter(
        PlayGame.is_active == True,
        PlayGame.hub_zone == zone,
    )
    if zone == ZONE_LEARNING:
        q = q.filter(PlayGame.is_public == True)
    q = q.order_by(PlayGame.sort_order)

    if zone == ZONE_LEARNING and not is_enabled(db, "play.hub", market=market):
        return []
    if zone == ZONE_REWARD and not is_enabled(db, "play.reward_playground", market=market):
        return []

    max_grade = min(5, max(1, settings.PLAY_MAX_GRADE))
    out: List[PublicGameItem] = []
    for game in q.all():
        if int(game.grade_min or 1) > max_grade:
            continue
        eff_max = min(int(game.grade_max or 5), max_grade)
        if grade is not None and not (int(game.grade_min or 1) <= grade <= eff_max):
            continue
        meta = game.meta_json or {}
        launch = game_launch_meta(game)
        out.append(
            PublicGameItem(
                id=game.id,
                display_name=game.display_name,
                game_type=game.game_type,
                hub_zone=game.hub_zone or zone,
                subject=game.subject,
                grade_min=int(game.grade_min or 1),
                grade_max=eff_max,
                launch_url=launch.get("launch_url"),
                icon=meta.get("icon"),
                tagline=meta.get("tagline"),
                min_client_version=launch.get("min_client_version") or "1.0.0",
                requires_wallet=bool(game.requires_wallet),
            )
        )
    return out

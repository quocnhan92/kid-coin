"""Kid engagement — first-play free pass & reward session counts."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.play.wallet import PlayWalletLedgerEntry

FIRST_PLAY_FREE_GAME_IDS = frozenset({"fly_shooter", "snake", "flappy"})
FEATURED_ONBOARD_ROUTE = "/game/english-shooter/lily"
MAX_FIRST_FREE_PLAYS = 3


def count_reward_play_sessions(db: Session, user_id: UUID) -> int:
    return (
        db.query(PlayWalletLedgerEntry)
        .filter(
            PlayWalletLedgerEntry.user_id == user_id,
            PlayWalletLedgerEntry.ref_reward_game_id.isnot(None),
        )
        .count()
    )


def is_first_play_free_eligible(db: Session, user_id: UUID | None) -> bool:
    if settings.PLAY_SKIP_REWARD_SPEND:
        return True
    if not user_id:
        return True
    return count_reward_play_sessions(db, user_id) < MAX_FIRST_FREE_PLAYS


def onboarding_payload(db: Session, user_id: UUID | None) -> dict:
    first_free = is_first_play_free_eligible(db, user_id)
    return {
        "featured_route": FEATURED_ONBOARD_ROUTE,
        "first_play_free": first_free,
        "hide_wallet_ui": first_free,
        "starter_game_ids": sorted(FIRST_PLAY_FREE_GAME_IDS),
    }

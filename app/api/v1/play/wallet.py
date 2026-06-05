from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps_play import require_kid
from app.models.user_family import User
from app.schemas.play import (
    PlayWalletOut,
    PlayWalletLedgerItem,
    SpendRewardPlayRequest,
    SpendRewardPlayResponse,
)
from app.services import play_reward_service
from app.services.play_wallet_service import (
    debit_reward_play,
    get_or_create_wallet,
    list_ledger,
    wallet_snapshot,
)

router = APIRouter()


@router.get("/wallet", response_model=PlayWalletOut)
def get_wallet(
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
):
    w = get_or_create_wallet(db, kid.id)
    db.commit()
    return PlayWalletOut(**wallet_snapshot(w))


@router.get("/wallet/ledger", response_model=list[PlayWalletLedgerItem])
def get_wallet_ledger(
    limit: int = 30,
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
):
    return [PlayWalletLedgerItem(**row) for row in list_ledger(db, kid.id, limit=limit)]


@router.post("/wallet/spend-reward-play", response_model=SpendRewardPlayResponse)
def spend_reward_play(
    body: SpendRewardPlayRequest,
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
):
    ok, msg, status = play_reward_service.validate_reward_play(
        db, kid.id, body.reward_game_id
    )
    if not ok:
        raise HTTPException(status_code=status, detail=msg)
    ok, msg, snap = debit_reward_play(
        db, kid.id, body.reward_game_id, session_id=body.session_id
    )
    if not ok:
        raise HTTPException(status_code=402, detail=msg)
    db.commit()
    return SpendRewardPlayResponse(
        ok=True,
        message=msg,
        wallet=PlayWalletOut(**snap) if snap else None,
    )

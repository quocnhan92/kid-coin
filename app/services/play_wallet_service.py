"""Ví điểm học/chơi — sổ cái kiểu ngân hàng cho bé."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.play_constants import (
    ACCOUNT_AVAILABLE,
    ACCOUNT_SPEND_REWARD,
    EARN_ACCOUNT_PREFIX,
    LEGACY_EARN_ACCOUNTS,
    LEARNING_GAME_IDS,
    POINTS_PER_CORRECT,
    REWARD_PLAY_COST,
    GAME_ENGLISH_SHOOTER,
    earn_account_for_game,
)
from app.models.play.wallet import PlayKidWallet, PlayWalletLedgerEntry

SYSTEM_ACCOUNTS = {ACCOUNT_AVAILABLE: 0, ACCOUNT_SPEND_REWARD: 0}


def _normalize_accounts(raw: Optional[Dict[str, Any]]) -> Dict[str, int]:
    """Gộp key cũ (EARN_MATH_VN) sang EARN:math_blast; giữ mọi EARN:* động."""
    out: Dict[str, int] = dict(SYSTEM_ACCOUNTS)
    if not raw:
        return out
    for k, v in raw.items():
        try:
            amt = int(v)
        except (TypeError, ValueError):
            continue
        target = LEGACY_EARN_ACCOUNTS.get(k, k)
        if target in SYSTEM_ACCOUNTS:
            out[target] = amt
        elif target.startswith(EARN_ACCOUNT_PREFIX) or k.startswith(EARN_ACCOUNT_PREFIX):
            out[target] = out.get(target, 0) + amt
    return out


def _merge_accounts(raw: Optional[Dict[str, Any]]) -> Dict[str, int]:
    return _normalize_accounts(raw)


def _total_earned_learning(accounts: Dict[str, int]) -> int:
    return sum(v for k, v in accounts.items() if k.startswith(EARN_ACCOUNT_PREFIX))


def get_or_create_wallet(db: Session, user_id: UUID) -> PlayKidWallet:
    row = db.query(PlayKidWallet).filter(PlayKidWallet.user_id == user_id).first()
    if row:
        return row
    row = PlayKidWallet(user_id=user_id, available_balance=0, accounts_json=SYSTEM_ACCOUNTS.copy())
    db.add(row)
    db.flush()
    return row


def wallet_snapshot(wallet: PlayKidWallet) -> Dict[str, Any]:
    accounts = _merge_accounts(wallet.accounts_json)
    return {
        "available_balance": int(wallet.available_balance or 0),
        "accounts": accounts,
        "total_earned_learning": _total_earned_learning(accounts),
        "total_spent_reward": accounts[ACCOUNT_SPEND_REWARD],
    }


def _append_ledger(
    db: Session,
    user_id: UUID,
    account_code: str,
    entry_type: str,
    amount: int,
    balance_after: int,
    *,
    ref_game_id: Optional[str] = None,
    ref_session_id: Optional[UUID] = None,
    ref_reward_game_id: Optional[str] = None,
    note: Optional[str] = None,
) -> None:
    db.add(
        PlayWalletLedgerEntry(
            user_id=user_id,
            account_code=account_code,
            entry_type=entry_type,
            amount=amount,
            balance_after=balance_after,
            ref_game_id=ref_game_id,
            ref_session_id=ref_session_id,
            ref_reward_game_id=ref_reward_game_id,
            note=note,
        )
    )


def credit_learning(
    db: Session,
    user_id: UUID,
    game_id: str,
    points: int,
    session_id: Optional[UUID] = None,
) -> Optional[Dict[str, Any]]:
    if points <= 0 or game_id not in LEARNING_GAME_IDS:
        return None
    earn_acct = earn_account_for_game(game_id)

    wallet = get_or_create_wallet(db, user_id)
    accounts = _normalize_accounts(wallet.accounts_json)
    accounts[earn_acct] = accounts.get(earn_acct, 0) + points
    avail = int(wallet.available_balance or 0) + points
    accounts[ACCOUNT_AVAILABLE] = avail
    wallet.available_balance = avail
    wallet.accounts_json = accounts
    wallet.updated_at = datetime.now(timezone.utc)

    _append_ledger(
        db, user_id, earn_acct, "credit", points, accounts[earn_acct],
        ref_game_id=game_id, ref_session_id=session_id,
        note=f"Learning credit ({game_id})",
    )
    _append_ledger(
        db, user_id, ACCOUNT_AVAILABLE, "credit", points, avail,
        ref_game_id=game_id, ref_session_id=session_id,
        note="To reward playground balance",
    )
    db.flush()
    return wallet_snapshot(wallet)


def debit_reward_play(
    db: Session,
    user_id: UUID,
    reward_game_id: str,
    *,
    session_id: Optional[UUID] = None,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    from app.core.config import settings

    cost = REWARD_PLAY_COST.get(reward_game_id)
    if cost is None:
        return False, "Unknown reward game", None

    wallet = get_or_create_wallet(db, user_id)
    if settings.PLAY_SKIP_REWARD_SPEND:
        return True, "ok (free play)", wallet_snapshot(wallet)
    avail = int(wallet.available_balance or 0)
    if avail < cost:
        return False, f"Need {cost} points (have {avail})", wallet_snapshot(wallet)

    accounts = _merge_accounts(wallet.accounts_json)
    avail -= cost
    accounts[ACCOUNT_AVAILABLE] = avail
    accounts[ACCOUNT_SPEND_REWARD] = accounts[ACCOUNT_SPEND_REWARD] + cost
    wallet.available_balance = avail
    wallet.accounts_json = accounts
    wallet.updated_at = datetime.now(timezone.utc)

    _append_ledger(
        db, user_id, ACCOUNT_AVAILABLE, "debit", cost, avail,
        ref_reward_game_id=reward_game_id, ref_session_id=session_id,
        note=f"Reward play: {reward_game_id}",
    )
    _append_ledger(
        db, user_id, ACCOUNT_SPEND_REWARD, "credit", cost, accounts[ACCOUNT_SPEND_REWARD],
        ref_reward_game_id=reward_game_id, ref_session_id=session_id,
        note="Lifetime reward spend",
    )
    db.flush()
    return True, "ok", wallet_snapshot(wallet)


def points_from_session_summary(game_id: str, correct_count: int, summary_json: Optional[dict]) -> int:
    if correct_count <= 0:
        return 0
    if game_id == GAME_ENGLISH_SHOOTER and summary_json:
        gold = int(summary_json.get("gold_earned") or 0)
        if gold > 0:
            return gold
    return correct_count * POINTS_PER_CORRECT


def list_ledger(db: Session, user_id: UUID, limit: int = 30) -> List[Dict[str, Any]]:
    rows = (
        db.query(PlayWalletLedgerEntry)
        .filter(PlayWalletLedgerEntry.user_id == user_id)
        .order_by(PlayWalletLedgerEntry.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "account_code": r.account_code,
            "entry_type": r.entry_type,
            "amount": int(r.amount),
            "balance_after": int(r.balance_after),
            "ref_game_id": r.ref_game_id,
            "ref_reward_game_id": r.ref_reward_game_id,
            "note": r.note,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

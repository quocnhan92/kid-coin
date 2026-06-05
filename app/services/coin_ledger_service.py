from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.logs_transactions import Transaction, TransactionType
from app.models.user_family import User


class InsufficientCoinsError(ValueError):
    pass


def credit(
    db: Session,
    user: User,
    amount: int,
    tx_type: TransactionType,
    description: str,
    reference_id: Optional[UUID] = None,
) -> int:
    if amount <= 0:
        raise ValueError("credit amount must be positive")
    user.current_coin = int(user.current_coin or 0) + amount
    db.add(
        Transaction(
            kid_id=user.id,
            amount=amount,
            transaction_type=tx_type,
            reference_id=reference_id,
            description=description,
        )
    )
    return int(user.current_coin)


def debit(
    db: Session,
    user: User,
    amount: int,
    tx_type: TransactionType,
    description: str,
    reference_id: Optional[UUID] = None,
) -> int:
    if amount <= 0:
        raise ValueError("debit amount must be positive")
    balance = int(user.current_coin or 0)
    if balance < amount:
        raise InsufficientCoinsError("Insufficient coins")
    user.current_coin = balance - amount
    db.add(
        Transaction(
            kid_id=user.id,
            amount=-amount,
            transaction_type=tx_type,
            reference_id=reference_id,
            description=description,
        )
    )
    return int(user.current_coin)


def adjust_admin(
    db: Session,
    user: User,
    amount: int,
    reason: str,
) -> int:
    if amount == 0:
        return int(user.current_coin or 0)
    if amount > 0:
        return credit(
            db,
            user,
            amount,
            TransactionType.ADMIN_ADJUSTMENT,
            f"Admin Adjustment: {reason}",
        )
    return debit(
        db,
        user,
        -amount,
        TransactionType.ADMIN_ADJUSTMENT,
        f"Admin Adjustment: {reason}",
    )


def snapshot(user: User) -> Dict[str, Any]:
    return {
        "user_id": str(user.id),
        "current_coin": int(user.current_coin or 0),
        "total_earned_score": int(user.total_earned_score or 0),
    }

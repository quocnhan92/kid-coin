from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_family import User, Role
from app.services.audit import AuditService
from app.api import deps
from app.models.logs_transactions import Transaction
from app.schemas import user as user_schemas
from uuid import UUID


router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    # Example Audit Log
    AuditService.log(
        db=db,
        user_id=None, # In a real scenario, get the current user ID
        action="VIEW_ALL_USERS",
        resource_type="User",
        details={"count": len(users)},
        ip_address="127.0.0.1"
    )
    return users


@router.get("/me", response_model=user_schemas.UserMeResponse)
def get_me(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Return current authenticated user info (used by kid dashboard UI).
    """
    # Role is an Enum; make it serialize as its value (e.g. "KID"/"PARENT")
    role_value = getattr(current_user.role, "value", str(current_user.role))
    return user_schemas.UserMeResponse(
        id=current_user.id,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=role_value,
        current_coin=int(current_user.current_coin),
        total_earned_score=int(current_user.total_earned_score),
    )


@router.get("/{kid_id}/history", response_model=list[user_schemas.TransactionItem])
def get_kid_history(
    kid_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Return transaction history for a kid.
    - KID can only view their own history.
    - PARENT can view kids in the same family.
    """
    kid = db.query(User).filter(User.id == kid_id).first()
    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")

    if current_user.role == Role.KID and current_user.id != kid_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.kid_id == kid_id)
        .order_by(Transaction.created_at.desc())
        .limit(50)
        .all()
    )
    return transactions

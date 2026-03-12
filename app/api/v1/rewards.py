from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyReward
from app.models.logs_transactions import Transaction, TransactionType, RedemptionLog
from app.models.user_family import User
from app.services.audit import AuditService, AuditStatus
from app.schemas import reward as reward_schemas

router = APIRouter()

@router.get("/", response_model=list[reward_schemas.RewardItem])
async def get_rewards(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get all active rewards for the family.
    """
    rewards = db.query(FamilyReward).filter(
        FamilyReward.family_id == current_user.family_id,
        FamilyReward.is_active == True,
        FamilyReward.is_deleted == False
    ).all()
    
    return rewards

@router.post("/{reward_id}/redeem", response_model=reward_schemas.RewardRedeemedResponse)
async def redeem_reward(
    reward_id: str,
    request: reward_schemas.RewardRedeemRequest,
    current_user: User = Depends(deps.require_role(deps.Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Redeem a reward if sufficient balance.
    """
    reward = db.query(FamilyReward).filter(
        FamilyReward.id == reward_id,
        FamilyReward.family_id == current_user.family_id,
        FamilyReward.is_active == True
    ).first()
    
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found or inactive")

    # 1. Check Balance
    if current_user.current_coin < reward.points_cost:
        raise HTTPException(status_code=400, detail="Insufficient coins")
        
    # 2. Check Stock (if limit exists)
    if reward.stock_limit is not None and reward.stock_limit <= 0:
         raise HTTPException(status_code=400, detail="Out of stock")

    try:
        # 3. Create Redemption Log
        redemption = RedemptionLog(
            kid_id=current_user.id,
            reward_id=reward.id,
            status="PENDING_DELIVERY"
        )
        db.add(redemption)
        db.flush() # get ID

        # 4. Create Transaction
        transaction = Transaction(
            kid_id=current_user.id,
            amount=-reward.points_cost,
            transaction_type=TransactionType.REWARD_REDEMPTION,
            reference_id=redemption.id,
            description=f"Redeemed: {reward.name}"
        )
        db.add(transaction)
        
        # 5. Update Balance & Stock
        current_user.current_coin -= reward.points_cost
        if reward.stock_limit is not None:
            reward.stock_limit -= 1

        db.commit()
        
        AuditService.log(
            db=db,
            action="REDEEM_REWARD",
            resource_type="RedemptionLog",
            resource_id=str(redemption.id),
            status=AuditStatus.SUCCESS,
            details={"cost": reward.points_cost}
        )
        
        return {
            "message": "Reward redeemed successfully!",
            "redemption_id": redemption.id,
            "points_deducted": reward.points_cost,
            "new_balance": current_user.current_coin
        }
    except Exception as e:
        db.rollback()
        AuditService.log_failed(
            db=db,
            action="REDEEM_REWARD",
            resource_type="Reward",
            resource_id=reward_id,
            error=e
        )
        raise HTTPException(status_code=500, detail="Redemption failed")

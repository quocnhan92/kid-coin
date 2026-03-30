from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyReward, MasterReward
from app.models.logs_transactions import Transaction, TransactionType, RedemptionLog, RedemptionStatus
from app.models.notifications import Notification, NotificationType
from app.models.user_family import User
from typing import List, Optional
from app.services.audit import AuditService, AuditStatus
from app.schemas import reward as reward_schemas
from datetime import date

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
            status=RedemptionStatus.PENDING_DELIVERY
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
        
        # 6. Generate Notification to Parents
        try:
            from app.models.notifications import Notification, NotificationType
            parents = db.query(User).filter(User.family_id == current_user.family_id, User.role == deps.Role.PARENT).all()
            for p in parents:
                notif = Notification(
                    user_id=p.id,
                    type=NotificationType.SYSTEM,
                    title="Đổi quà mới 🎁",
                    content=f"{current_user.display_name} vừa đổi món quà '{reward.name}'. Bạn hãy chuẩn bị quà nhé!",
                    reference_id=str(redemption.id),
                    action_data={"tab": "pending", "kid_id": str(current_user.id)}
                )
                db.add(notif)
            db.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send notification for reward redemption: {e}")


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

@router.put("/delivery/{redemption_id}")
async def deliver_reward(
    redemption_id: str,
    request: reward_schemas.DeliveryRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Confirm delivery of a reward.
    """
    log = db.query(RedemptionLog).filter(RedemptionLog.id == redemption_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Redemption log not found")
        
    kid = db.query(User).get(log.kid_id)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized for this log")

    if log.status != RedemptionStatus.PENDING_DELIVERY:
         raise HTTPException(status_code=400, detail="Reward already delivered")

    if request.status != "DELIVERED":
        raise HTTPException(status_code=400, detail="Invalid status update")

    try:
        from datetime import datetime
        log.status = RedemptionStatus.DELIVERED
        log.delivered_at = datetime.now()
        
        db.commit()
        
        try:
            from app.models.notifications import Notification, NotificationType
            reward = db.query(FamilyReward).get(log.reward_id)
            kid_notif = Notification(
                user_id=kid.id,
                type=NotificationType.SYSTEM,
                title="Quà đã về! 🎁",
                content=f"Bố/mẹ đã giao cho bạn món quà '{reward.name}'. Bạn đã nhận được chưa?",
                reference_id=str(log.id),
                action_data={"tab": "shop", "show_delivery_modal": True, "reward_name": reward.name}
            )
            db.add(kid_notif)
            db.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send delivery notification to kid: {e}")

        AuditService.log(
            db=db,
            action="DELIVER_REWARD",
            resource_type="RedemptionLog",
            resource_id=str(log.id),
            status=AuditStatus.SUCCESS
        )
        
        return {"status": "success", "message": "Reward marked as delivered"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(
            db=db,
            action="DELIVER_REWARD",
            resource_type="RedemptionLog",
            resource_id=redemption_id,
            error=e
        )
        raise HTTPException(status_code=500, detail="Delivery confirmation failed")

@router.get("/master", response_model=List[reward_schemas.MasterRewardResponse])
async def get_master_rewards(
    q: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Get suggested master rewards with search and age prioritization.
    """
    query = db.query(MasterReward)
    if q:
        query = query.filter(MasterReward.name.ilike(f"%{q}%"))
    
    rewards = query.all()
    
    # Age-based prioritization
    if current_user.birth_date:
        today = date.today()
        age = today.year - current_user.birth_date.year - ((today.month, today.day) < (current_user.birth_date.month, current_user.birth_date.day))
        
        def sort_key(r):
            # Tasks within age range get priority 0, outside get priority 1
            is_in_range = (r.min_age <= age <= r.max_age)
            return (0 if is_in_range else 1, r.name)
            
        rewards.sort(key=sort_key)
        
    return rewards

@router.post("/propose-master", response_model=dict)
async def propose_master_reward(
    request: reward_schemas.RewardProposeRequest,
    current_user: User = Depends(deps.require_role(deps.Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Propose a master reward to parents.
    """
    master = db.query(MasterReward).get(request.master_reward_id)
    if not master:
        raise HTTPException(status_code=404, detail="Master reward not found")
        
    try:
        parents = db.query(User).filter(User.family_id == current_user.family_id, User.role == deps.Role.PARENT).all()
        for p in parents:
            notif = Notification(
                user_id=p.id,
                type=NotificationType.SYSTEM,
                title="Con ước món quà mới! 🎁",
                content=f"{current_user.display_name} vừa ước món quà '{master.name}'. Bạn hãy xem và thêm vào cửa hàng nhé!",
                reference_id=str(master.id),
                action_data={"tab": "shop", "master_reward_id": master.id, "suggested_name": master.name}
            )
            db.add(notif)
        db.commit()
        
        AuditService.log(
            db=db,
            action="PROPOSE_REWARD",
            resource_type="MasterReward",
            resource_id=str(master.id),
            status=AuditStatus.SUCCESS
        )
        
        return {"status": "success", "message": "Đã gửi điều ước tới bố mẹ! ✨"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="PROPOSE_REWARD", resource_type="MasterReward", error=e)
        raise HTTPException(status_code=500, detail="Could not propose reward")

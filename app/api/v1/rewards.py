from fastapi import APIRouter, Depends, HTTPException, status
import logging
import traceback
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
    ).with_for_update().first()
    
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

@router.get("/master", response_model=List[reward_schemas.MasterRewardResponse])
async def get_master_rewards(
    q: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all master rewards for suggestions with age-based prioritization.
    """
    try:
        query = db.query(MasterReward)
        if q:
            query = query.filter(MasterReward.name.ilike(f"%{q}%"))

        rewards = query.all()

        # BUG-02 FIX: Age-based sort was dead code (return was before it). Moved correctly.
        if current_user.birth_date:
            today = date.today()
            age = today.year - current_user.birth_date.year - (
                (today.month, today.day) < (current_user.birth_date.month, current_user.birth_date.day)
            )

            def sort_key(r):
                min_a = r.min_age if r.min_age is not None else 0
                max_a = r.max_age if r.max_age is not None else 100
                is_in_range = (min_a <= age <= max_a)
                return (0 if is_in_range else 1, r.name)

            rewards.sort(key=sort_key)

        return [
            reward_schemas.MasterRewardResponse(
                master_reward_id=r.id,
                name=r.name,
                icon_url=r.icon_url,
                suggested_cost=r.suggested_cost or 50,
                min_age=r.min_age or 3,
                max_age=r.max_age or 18
            ) for r in rewards
        ]
    except Exception as e:
        logging.error(f"Error in get_master_rewards: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Debug Error: {str(e)}")

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
        
    # Check for existing pending proposal notification for same master reward from this kid
    # to avoid spamming the parent.
    existing_notif = db.query(Notification).filter(
        Notification.type == NotificationType.SYSTEM,
        Notification.reference_id == str(master.id),
        Notification.content.like(f"{current_user.display_name}%"),
        Notification.is_read == False
    ).first()
    
    if existing_notif:
        return {"status": "success", "message": "Bố mẹ đang xem xét yêu cầu này rồi! Bạn chờ chút nhé ✨"}

    try:
        parents = db.query(User).filter(User.family_id == current_user.family_id, User.role == deps.Role.PARENT).all()
        for p in parents:
            notif = Notification(
                user_id=p.id,
                type=NotificationType.SYSTEM,
                title="Con ước món quà mới! 🎁",
                content=f"{current_user.display_name} vừa ước món quà '{master.name}'. Bạn hãy xem và thêm vào cửa hàng nhé!",
                reference_id=str(master.id),
                action_data={"tab": "rewards", "master_reward_id": master.id, "suggested_name": master.name}
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

@router.get("/proposals", response_model=List[dict])
async def get_my_proposals(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Get my pending reward proposals. PARENT: returns empty list.
    """
    # Simply return empty for non-kid users to avoid dashboard errors
    if current_user.role != deps.Role.KID:
        return []
    # Simply fetch from Notifications of type REWARD_PROPOSAL sent by this kid
    # Or keep track in a separate table? Currently it's in Notifications with reference_id = master_id.
    # To keep it simple, we can query notifications where user is parent and sender is kid?
    # Actually, let's find notifications where reference_id is a MasterReward and user is a parent in this family.
    
    proposals = db.query(Notification).filter(
        Notification.type == NotificationType.SYSTEM,
        Notification.title.like("%ước món quà mới%"),
        Notification.content.like(f"{current_user.display_name}%")
    ).all()
    
    # Extract unique master IDs and names from content/action_data
    results = []
    seen_ids = set()
    for n in proposals:
        m_id = n.action_data.get("master_reward_id") if n.action_data else None
        if m_id and m_id not in seen_ids:
            seen_ids.add(m_id)
            results.append({
                "master_reward_id": m_id,
                "name": n.action_data.get("suggested_name") or "Quà ẩn danh",
                "status": "Đang chờ duyệt"
            })
    return results

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api import deps
from app.models.user_family import User, Role
from app.models.gamification import AvatarItem, UserAvatarItem, UserStreak, ItemType
from app.models.logs_transactions import Transaction, TransactionType
from app.schemas.gamification import LevelInfoResponse, StreakResponse, AvatarItemResponse, UserInventoryResponse
from app.services import gamification_service, streak_service

router = APIRouter()

@router.get("/me/level", response_model=LevelInfoResponse)
async def get_my_level(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get level and XP info for the current kid."""
    if current_user.role != Role.KID:
        raise HTTPException(status_code=403, detail="Only kids have levels.")
    return gamification_service.get_level_info(db, current_user)

@router.get("/me/streak", response_model=StreakResponse)
async def get_my_streak(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get current streak info for the kid."""
    streak = db.query(UserStreak).filter(UserStreak.user_id == current_user.id).first()
    if not streak:
        return StreakResponse(
            current_streak=0, 
            longest_streak=0, 
            last_active_date=None, 
            streak_bonus_active=False
        )
    return streak

@router.get("/shop", response_model=List[AvatarItemResponse])
async def get_avatar_shop(
    item_type: Optional[ItemType] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List items in the avatar shop."""
    query = db.query(AvatarItem).filter(AvatarItem.is_active == True)
    if item_type:
        query = query.filter(AvatarItem.item_type == item_type)
    
    items = query.all()
    
    # Check what items the user already owns
    owned_item_ids = [ua.item_id for ua in db.query(UserAvatarItem.item_id).filter(UserAvatarItem.user_id == current_user.id).all()]
    
    return [
        AvatarItemResponse(
            **item.__dict__,
            is_owned=(item.id in owned_item_ids)
        ) for item in items
    ]

@router.post("/shop/buy/{item_id}")
async def buy_avatar_item(
    item_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Purchase an item from the shop."""
    item = db.query(AvatarItem).filter(AvatarItem.id == item_id, AvatarItem.is_active == True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Check if already owned
    existing = db.query(UserAvatarItem).filter(
        UserAvatarItem.user_id == current_user.id,
        UserAvatarItem.item_id == item_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already own this item")
        
    # Check level requirement
    lv_info = gamification_service.get_level_info(db, current_user)
    if lv_info["current_level"] < item.min_level:
        raise HTTPException(
            status_code=403, 
            detail=f"You need to be Level {item.min_level} to buy this!"
        )
        
    # Check balance
    if current_user.current_coin < item.price_coins:
        raise HTTPException(status_code=400, detail="Insufficient coins")
        
    try:
        # 1. Deduct coins
        current_user.current_coin -= item.price_coins
        
        # 2. Add to inventory
        ua = UserAvatarItem(
            user_id=current_user.id,
            item_id=item.id
        )
        db.add(ua)
        
        # 3. Create transaction
        transaction = Transaction(
            kid_id=current_user.id,
            amount=-item.price_coins,
            transaction_type=TransactionType.AVATAR_PURCHASE,
            description=f"Bought: {item.name}"
        )
        db.add(transaction)
        
        db.commit()
        return {"status": "success", "message": f"Successfully bought {item.name}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory", response_model=List[UserInventoryResponse])
async def get_my_inventory(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """View owned avatar items."""
    inventory = db.query(UserAvatarItem, AvatarItem).join(
        AvatarItem, UserAvatarItem.item_id == AvatarItem.id
    ).filter(UserAvatarItem.user_id == current_user.id).all()
    
    return [
        UserInventoryResponse(
            id=str(ua.id),
            item_id=ua.item_id,
            name=item.name,
            item_type=item.item_type,
            image_url=item.image_url,
            is_equipped=ua.is_equipped,
            purchased_at=ua.purchased_at
        ) for ua, item in inventory
    ]

@router.post("/inventory/equip/{ua_id}")
async def equip_item(
    ua_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Equip or unequip an item."""
    ua = db.query(UserAvatarItem).filter(
        UserAvatarItem.id == ua_id,
        UserAvatarItem.user_id == current_user.id
    ).first()
    
    if not ua:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
        
    item = db.query(AvatarItem).get(ua.item_id)
    
    # If equipping, unequip others of the same type
    if not ua.is_equipped:
        equipped_others = db.query(UserAvatarItem).join(AvatarItem).filter(
            UserAvatarItem.user_id == current_user.id,
            AvatarItem.item_type == item.item_type,
            UserAvatarItem.is_equipped == True
        ).all()
        
        for eo in equipped_others:
            eo.is_equipped = False
            
        ua.is_equipped = True
    else:
        ua.is_equipped = False
        
    db.commit()
    return {"status": "success", "is_equipped": ua.is_equipped}

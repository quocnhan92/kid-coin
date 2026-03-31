from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class RewardBase(BaseModel):
    name: str
    points_cost: int
    stock_limit: Optional[int] = None
    icon_url: Optional[str] = None

class RewardItem(RewardBase):
    id: UUID
    family_id: UUID
    is_active: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RewardRedeemRequest(BaseModel):
    pass # No body needed for now, maybe quantity later

class RewardRedeemedResponse(BaseModel):
    message: str
    redemption_id: UUID
    points_deducted: int
    new_balance: int

class DeliveryRequest(BaseModel):
    status: str # DELIVERED

class MasterRewardResponse(BaseModel):
    master_reward_id: int
    name: str
    icon_url: Optional[str]
    suggested_cost: int
    min_age: int
    max_age: int

    class Config:
        from_attributes = True

class RewardProposeRequest(BaseModel):
    master_reward_id: int

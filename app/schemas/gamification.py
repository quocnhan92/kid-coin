from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from app.models.gamification import ItemType

class LevelInfoResponse(BaseModel):
    current_level: int
    level_name: str
    current_xp: int
    next_level_xp: Optional[int]
    xp_to_next_level: int
    progress_percentage: float

class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_active_date: Optional[date]
    streak_bonus_active: bool

class AvatarItemResponse(BaseModel):
    id: int
    name: str
    item_type: ItemType
    image_url: str
    price_coins: int
    min_level: int
    is_active: bool
    is_owned: bool = False

    class Config:
        from_attributes = True

class AvatarItemCreate(BaseModel):
    name: str
    item_type: ItemType
    image_url: str
    price_coins: int
    min_level: int = 1
    is_active: bool = True

class AvatarItemUpdate(BaseModel):
    name: Optional[str] = None
    item_type: Optional[ItemType] = None
    image_url: Optional[str] = None
    price_coins: Optional[int] = None
    min_level: Optional[int] = None
    is_active: Optional[bool] = None

class UserLevelBase(BaseModel):
    level: int
    name: str
    min_xp: int
    description: Optional[str] = None

class UserLevelCreate(UserLevelBase):
    pass

class UserLevelUpdate(BaseModel):
    level: Optional[int] = None
    name: Optional[str] = None
    min_xp: Optional[int] = None
    description: Optional[str] = None

class UserLevelResponse(UserLevelBase):
    id: int

    class Config:
        from_attributes = True

class UserInventoryResponse(BaseModel):
    id: str # UUID
    item_id: int
    name: str
    item_type: ItemType
    image_url: str
    is_equipped: bool
    purchased_at: datetime

    class Config:
        from_attributes = True

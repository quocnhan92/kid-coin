from pydantic import BaseModel
from typing import Optional
from app.models.tasks_rewards import Category, VerificationType

class MasterTaskBase(BaseModel):
    name: str
    icon_url: Optional[str] = None
    suggested_value: int = 10
    min_age: int = 3
    max_age: int = 18
    category: Category
    verification_type: VerificationType = VerificationType.REQUIRE_PHOTO

class MasterTaskCreate(MasterTaskBase):
    pass

class MasterTaskUpdate(BaseModel):
    name: Optional[str] = None
    icon_url: Optional[str] = None
    suggested_value: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    category: Optional[Category] = None
    verification_type: Optional[VerificationType] = None

class MasterTaskResponse(MasterTaskBase):
    id: int

    class Config:
        from_attributes = True

class MasterRewardBase(BaseModel):
    name: str
    icon_url: Optional[str] = None
    suggested_cost: int = 50
    min_age: int = 3
    max_age: int = 18

class MasterRewardCreate(MasterRewardBase):
    pass

class MasterRewardUpdate(BaseModel):
    name: Optional[str] = None
    icon_url: Optional[str] = None
    suggested_cost: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

class MasterRewardResponse(MasterRewardBase):
    id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserMeResponse(BaseModel):
    id: UUID
    display_name: str
    avatar_url: Optional[str]
    role: str
    current_coin: int
    total_earned_score: int

    class Config:
        from_attributes = True


class TransactionItem(BaseModel):
    id: UUID
    amount: int
    transaction_type: str
    reference_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


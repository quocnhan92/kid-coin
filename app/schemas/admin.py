from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.admin import AdminRole

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str

class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    display_name: str
    role: AdminRole
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True

class FamilyAdminResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str]
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

class CoinAdjustmentRequest(BaseModel):
    user_id: UUID
    amount: int
    reason: str

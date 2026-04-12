from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from app.models.social import ChallengeStatus, ClubRole

# --- Wall of Fame ---
class WallPostResponse(BaseModel):
    id: UUID
    kid_id: UUID
    kid_display_name: str
    kid_avatar_url: Optional[str]
    posted_by_name: str
    image_url: Optional[str]
    caption: str
    likes_count: int
    is_liked_by_me: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class WallPostCreate(BaseModel):
    kid_id: UUID
    image_url: Optional[str] = None
    caption: str

# --- Family Challenge ---
class FamilyChallengeBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_count: int
    duration_days: int
    reward_coins: int
    start_date: date
    end_date: date

class FamilyChallengeCreate(FamilyChallengeBase):
    pass

class ChallengeProgressResponse(BaseModel):
    user_id: UUID
    check_in_date: date
    proof_image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FamilyChallengeResponse(FamilyChallengeBase):
    id: UUID
    status: ChallengeStatus
    current_progress: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChallengeCheckInRequest(BaseModel):
    proof_image_url: Optional[str] = None

# --- Teen Mode ---
class TeenModeToggleRequest(BaseModel):
    is_teen_mode: bool

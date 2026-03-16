from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Pydantic model for Club data returned by the API
class Club(BaseModel):
    id: UUID
    name: str
    creator_family_id: UUID
    invite_code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True # Allows creating Pydantic model from ORM object

class ClubCreateRequest(BaseModel):
    name: str

class ClubJoinRequest(BaseModel):
    invite_code: str

class ClubMember(BaseModel):
    kid_id: UUID
    display_name: str
    avatar_url: Optional[str] = None
    total_earned_score: int

    class Config:
        from_attributes = True

class Leaderboard(BaseModel):
    club_name: str
    members: List[ClubMember]

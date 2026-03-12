from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import enum

# --- Enums ---
class ClubRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

# --- Base Schemas ---

class ClubBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class ClubTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    points_reward: int

# --- Request Schemas ---

class ClubCreateRequest(ClubBase):
    custom_invite_code: Optional[str] = None

class ClubUpdateRequest(ClubBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class ClubJoinRequest(BaseModel):
    invite_code: str
    user_ids: List[UUID]

class ClubAddMemberRequest(BaseModel):
    username: Optional[str] = None # For adding other parents
    user_id: Optional[UUID] = None # For adding kids directly if ID is known
    role: ClubRole = ClubRole.MEMBER

class ClubTaskCreateRequest(ClubTaskBase):
    due_date: Optional[datetime] = None

class ClubTaskUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_reward: Optional[int] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None

# --- Response Schemas ---

class ClubMemberResponse(BaseModel):
    user_id: UUID # Changed from kid_id
    display_name: str
    avatar_url: Optional[str] = None
    total_earned_score: int
    role: ClubRole
    user_global_role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class ClubTaskResponse(ClubTaskBase):
    id: UUID
    club_id: UUID
    due_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ClubResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    creator_family_id: UUID
    invite_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClubDetailResponse(ClubResponse):
    members: List[ClubMemberResponse] = []
    tasks: List[ClubTaskResponse] = []

class Leaderboard(BaseModel):
    club_name: str
    members: List[ClubMemberResponse]

class ClubInvitationResponse(BaseModel):
    id: UUID
    club_id: UUID
    invited_user_id: UUID
    inviter_id: Optional[UUID]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class InvitationRespondRequest(BaseModel):
    action: str  # ACCEPT or REJECT


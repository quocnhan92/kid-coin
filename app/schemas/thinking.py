from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from app.models.thinking import BidStatus, ProblemStatus, SolutionStatus, ReflectionStatus

# --- Task Bidding ---
class TaskBidBase(BaseModel):
    title: str
    description: Optional[str] = None
    proposed_coins: int

class TaskBidCreate(TaskBidBase):
    pass

class TaskBidResponse(TaskBidBase):
    id: UUID
    kid_id: UUID
    final_coins: Optional[int]
    status: BidStatus
    parent_comment: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class TaskBidRespondRequest(BaseModel):
    action: str # "ACCEPT", "REJECT", "COUNTER"
    comment: Optional[str] = None
    counter_price: Optional[int] = None

# --- Problem Board ---
class ProblemBoardBase(BaseModel):
    title: str
    description: Optional[str] = None
    reward_coins: int
    deadline: Optional[datetime] = None

class ProblemBoardCreate(ProblemBoardBase):
    pass

class ProblemSolutionResponse(BaseModel):
    id: UUID
    kid_id: UUID
    task_description: str
    status: SolutionStatus
    proof_image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProblemBoardResponse(ProblemBoardBase):
    id: UUID
    status: ProblemStatus
    created_at: datetime
    solutions: List[ProblemSolutionResponse] = []

    class Config:
        from_attributes = True

class SolutionSubmitRequest(BaseModel):
    task_description: str
    proof_image_url: Optional[str] = None

# --- Weekly Reflection ---
class WeeklyReflectionBase(BaseModel):
    q1_answer: Optional[str] = None
    q2_answer: Optional[str] = None
    q3_answer: Optional[str] = None

class WeeklyReflectionSubmit(WeeklyReflectionBase):
    pass

class WeeklyReflectionResponse(WeeklyReflectionBase):
    id: UUID
    week_start: date
    bonus_coins: int
    status: ReflectionStatus
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReflectionRewardRequest(BaseModel):
    bonus_coins: int
    comment: Optional[str] = None

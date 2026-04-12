from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from app.models.teen import ContractStatus, PeriodType, ProjectStatus, MilestoneStatus

# --- Teen Contract ---
class TeenContractBase(BaseModel):
    title: str
    description: str
    period_type: Optional[PeriodType] = None
    start_date: date
    end_date: date
    salary_coins: int
    milestones: Optional[dict] = None

class TeenContractCreate(TeenContractBase):
    pass

class TeenContractResponse(TeenContractBase):
    id: UUID
    kid_id: UUID
    status: ContractStatus
    signed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ContractCheckinRequest(BaseModel):
    note: Optional[str] = None
    proof_url: Optional[str] = None

# --- Personal Project ---
class PersonalProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    total_budget: int
    milestones: List[dict] # Expected format: [{"name": "Step 1", "reward": 100}, ...]

class PersonalProjectCreate(PersonalProjectBase):
    pass

class PersonalProjectResponse(PersonalProjectBase):
    id: UUID
    kid_id: UUID
    status: ProjectStatus
    created_at: datetime

    class Config:
        from_attributes = True

class MilestoneSubmitRequest(BaseModel):
    note: Optional[str] = None
    proof_url: Optional[str] = None

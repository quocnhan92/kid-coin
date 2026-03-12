from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.logs_transactions import TaskStatus

class QuestBase(BaseModel):
    name: str
    points_reward: int
    icon_url: Optional[str] = None

class QuestItem(QuestBase):
    id: UUID
    task_id: UUID
    status: Optional[TaskStatus] = None # None means not started
    proof_image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestSubmitRequest(BaseModel):
    proof_image_url: Optional[str] = None

class QuestVerifyRequest(BaseModel):
    action: str # APPROVE or REJECT
    comment: Optional[str] = None

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.logs_transactions import TaskStatus
from app.models.tasks_rewards import VerificationType

class QuestBase(BaseModel):
    master_task_id: Optional[int] = None
    name: str
    points_reward: Optional[int] = 0
    icon_url: Optional[str] = None
    min_age: Optional[int] = 3
    max_age: Optional[int] = 18

class QuestItem(QuestBase):
    log_id: Optional[UUID] = None
    task_id: UUID
    status: Optional[TaskStatus] = None # None means not started
    proof_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    verification_type: Optional[str] = None

    class Config:
        from_attributes = True

class QuestSubmitRequest(BaseModel):
    proof_image_url: Optional[str] = None

class QuestVerifyRequest(BaseModel):
    action: str # APPROVE or REJECT
    comment: Optional[str] = None

class QuestProposeRequest(BaseModel):
    master_task_id: int

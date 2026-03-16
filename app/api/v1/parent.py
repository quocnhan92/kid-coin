from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyTask
from app.models.logs_transactions import TaskLog, TaskStatus
from app.models.user_family import User, Role
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class PendingTaskResponse(BaseModel):
    log_id: UUID
    kid_name: str
    kid_avatar: Optional[str]
    task_name: str
    points_reward: int
    proof_image_url: Optional[str]
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

@router.get("/pending-tasks", response_model=List[PendingTaskResponse])
async def get_pending_tasks(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all pending tasks for kids in the parent's family.
    """
    
    # Query pending logs for kids in the same family
    pending_logs = db.query(TaskLog, User, FamilyTask).join(
        User, TaskLog.kid_id == User.id
    ).join(
        FamilyTask, TaskLog.task_id == FamilyTask.id
    ).filter(
        User.family_id == current_user.family_id,
        TaskLog.status == TaskStatus.PENDING_APPROVAL
    ).order_by(TaskLog.created_at.desc()).all()
    
    response = []
    for log, kid, task in pending_logs:
        response.append(PendingTaskResponse(
            log_id=log.id,
            kid_name=kid.display_name,
            kid_avatar=kid.avatar_url,
            task_name=task.name,
            points_reward=task.points_reward,
            proof_image_url=log.proof_image_url,
            created_at=log.created_at,
            status=log.status
        ))
        
    return response

@router.get("/kids")
async def get_kids(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all kids in the family with their current coin balance.
    """
    kids = db.query(User).filter(
        User.family_id == current_user.family_id,
        User.role == Role.KID
    ).all()
    
    return [
        {
            "id": kid.id,
            "display_name": kid.display_name,
            "avatar_url": kid.avatar_url,
            "current_coin": kid.current_coin,
            "total_earned_score": kid.total_earned_score
        }
        for kid in kids
    ]

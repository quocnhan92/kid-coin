from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyTask, FamilyReward
from app.models.logs_transactions import TaskLog, TaskStatus, RedemptionLog, RedemptionStatus
from app.models.user_family import User, Role
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.services.audit import AuditService, AuditStatus

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

class PendingRedemptionResponse(BaseModel):
    redemption_id: UUID
    kid_name: str
    kid_avatar: Optional[str]
    reward_name: str
    points_cost: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class FamilyTaskResponse(BaseModel):
    id: UUID
    name: str
    points_reward: int
    is_active: bool
    created_at: datetime

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
    pending_logs = db.query(TaskLog, User, FamilyTask).join(
        User, TaskLog.kid_id == User.id
    ).join(
        FamilyTask, TaskLog.family_task_id == FamilyTask.id # Changed to family_task_id based on recent DB updates
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

@router.get("/pending-redemptions", response_model=List[PendingRedemptionResponse])
async def get_pending_redemptions(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all pending rewards waiting for delivery to kids.
    """
    pending_logs = db.query(RedemptionLog, User, FamilyReward).join(
        User, RedemptionLog.kid_id == User.id
    ).join(
        FamilyReward, RedemptionLog.reward_id == FamilyReward.id
    ).filter(
        User.family_id == current_user.family_id,
        RedemptionLog.status == RedemptionStatus.PENDING_DELIVERY
    ).order_by(RedemptionLog.created_at.desc()).all()
    
    response = []
    for log, kid, reward in pending_logs:
        response.append(PendingRedemptionResponse(
            redemption_id=log.id,
            kid_name=kid.display_name,
            kid_avatar=kid.avatar_url,
            reward_name=reward.name,
            points_cost=reward.points_cost,
            created_at=log.created_at,
            status=log.status
        ))
        
    return response

@router.get("/tasks", response_model=List[FamilyTaskResponse])
async def get_family_tasks(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all tasks for the family to manage.
    """
    tasks = db.query(FamilyTask).filter(
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_deleted == False
    ).order_by(FamilyTask.created_at.desc()).all()
    
    return tasks

@router.put("/tasks/{task_id}/toggle")
async def toggle_family_task(
    task_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Toggle a family task's active status.
    """
    task = db.query(FamilyTask).filter(
        FamilyTask.id == task_id,
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_deleted == False
    ).first()
    
    if not task:
         raise HTTPException(status_code=404, detail="Task not found")
         
    task.is_active = not task.is_active
    db.commit()
    return {"status": "success", "is_active": task.is_active}

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

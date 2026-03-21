from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyTask
from app.models.logs_transactions import TaskLog, TaskStatus
from app.models.user_family import User
from app.models.audit import AuditStatus
from app.services.audit import AuditService
from app.schemas import quest as quest_schemas
from typing import List
from datetime import datetime, date

router = APIRouter()

@router.get("/daily", response_model=List[quest_schemas.QuestItem])
async def get_daily_quests(
    current_user: User = Depends(deps.require_role(deps.Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Get daily quests for the kid.
    """
    # 1. Get all active tasks for the family
    active_tasks = db.query(FamilyTask).filter(
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_active == True,
        FamilyTask.is_deleted == False
    ).all()

    # 2. Check if the kid has already submitted or completed any today
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    quests = []
    for task in active_tasks:
        log = db.query(TaskLog).filter(
            TaskLog.family_task_id == task.id,
            TaskLog.kid_id == current_user.id,
            TaskLog.created_at >= today_start
        ).order_by(TaskLog.created_at.desc()).first()
        
        quest_item = quest_schemas.QuestItem(
            id=log.id if log else None, # Log ID if submitted, else None
            task_id=task.id,
            name=task.name,
            points_reward=task.points_reward,
            status=log.status if log else None,
            proof_image_url=log.proof_image_url if log else None,
            created_at=log.created_at if log else None
        )
        quests.append(quest_item)
        
    return quests

@router.post("/{task_id}/submit", response_model=quest_schemas.QuestItem)
async def submit_quest(
    task_id: str,
    request: quest_schemas.QuestSubmitRequest,
    current_user: User = Depends(deps.require_role(deps.Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """
    KID: Submit a quest for approval.
    """
    # 1. Validate task
    task = db.query(FamilyTask).filter(
        FamilyTask.id == task_id,
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_active == True
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or inactive")

    # 2. Check if already submitted today
    today_start = datetime.combine(date.today(), datetime.min.time())
    existing_log = db.query(TaskLog).filter(
        TaskLog.family_task_id == task.id,
        TaskLog.kid_id == current_user.id,
        TaskLog.created_at >= today_start
    ).order_by(TaskLog.created_at.desc()).first()
    
    # Allow re-submit only if the latest attempt was rejected.
    if existing_log and existing_log.status != TaskStatus.REJECTED:
        raise HTTPException(status_code=400, detail="Task already submitted today")

    # 3. Create Task Log
    try:
        new_log = TaskLog(
            kid_id=current_user.id,
            family_task_id=task.id,
            status=TaskStatus.PENDING_APPROVAL,
            proof_image_url=request.proof_image_url
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        # 4. Audit Log
        AuditService.log(
            db=db,
            action="SUBMIT_QUEST",
            resource_type="TaskLog",
            resource_id=str(new_log.id),
            status=AuditStatus.SUCCESS,
            details={"task_name": task.name}
        )
        
        return quest_schemas.QuestItem(
            id=new_log.id,
            task_id=task.id,
            name=task.name,
            points_reward=task.points_reward,
            status=new_log.status,
            proof_image_url=new_log.proof_image_url,
            created_at=new_log.created_at
        )
    except Exception as e:
        db.rollback()
        AuditService.log_failed(
            db=db,
            action="SUBMIT_QUEST",
            resource_type="TaskLog",
            error=e,
            details={"task_id": task_id}
        )
        raise HTTPException(status_code=500, detail="Failed to submit quest")

@router.post("/{log_id}/verify")
async def verify_quest(
    log_id: str,
    request: quest_schemas.QuestVerifyRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Approve or Reject a quest submission.
    """
    # 1. Get the log
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    # verify ownership via kid's family
    kid = db.query(User).get(log.kid_id)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized for this submission")

    if log.status != TaskStatus.PENDING_APPROVAL:
         raise HTTPException(status_code=400, detail="Submission already processed")

    # 2. Process Approval/Rejection
    try:
        log.resolved_at = datetime.now()
        
        if request.action == "APPROVE":
            log.status = TaskStatus.APPROVED
            
            # Transaction: Add Coin & XP
            task = db.query(FamilyTask).get(log.family_task_id)
            points = task.points_reward
            
            from app.models.logs_transactions import Transaction, TransactionType
            
            transaction = Transaction(
                kid_id=kid.id,
                amount=points,
                transaction_type=TransactionType.TASK_COMPLETION,
                reference_id=log.id,
                description=f"Approved: {task.name}"
            )
            db.add(transaction)
            
            # Update User Balances
            kid.current_coin += points
            kid.total_earned_score += points
            
            AuditService.log(
                db=db,
                action="APPROVE_QUEST",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS,
                details={"points_awarded": points}
            )
            
        elif request.action == "REJECT":
            log.status = TaskStatus.REJECTED
            AuditService.log(
                db=db,
                action="REJECT_QUEST",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS,
                details={"reason": request.comment}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        db.commit()
        return {"status": "success", "message": f"Quest {request.action.lower()}ed"}
        
    except Exception as e:
        db.rollback()
        AuditService.log_failed(
            db=db,
            action="VERIFY_QUEST",
            resource_type="TaskLog",
            resource_id=str(log_id),
            error=e
        )
        raise HTTPException(status_code=500, detail="Verification failed")

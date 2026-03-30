from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyTask, VerificationType, MasterTask
from app.models.logs_transactions import TaskLog, TaskStatus
from app.models.user_family import User, Role
from app.models.audit import AuditStatus
from app.services.audit import AuditService
from app.schemas import quest as quest_schemas
from typing import List, Optional
from datetime import datetime, date

router = APIRouter()

@router.get("/daily", response_model=List[quest_schemas.QuestItem])
async def get_daily_quests(
    current_user: User = Depends(deps.get_current_user), # Changed to get_current_user
    db: Session = Depends(deps.get_db)
):
    """
    Get daily quests for the current user (Kid or Parent).
    """
    # 1. Get all active tasks for the family
    active_tasks = db.query(FamilyTask).filter(
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_active == True,
        FamilyTask.is_deleted == False
    ).all()

    # 2. Check if the user has already submitted or completed any today
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
            created_at=log.created_at if log else None,
            verification_type=task.verification_type.value if task.verification_type else None,
            parent_comment=log.parent_comment if log else None # Include comment for kid to see
        )
        quests.append(quest_item)
        
    return quests

@router.post("/{task_id}/submit", response_model=quest_schemas.QuestItem)
async def submit_quest(
    task_id: str,
    request: quest_schemas.QuestSubmitRequest,
    current_user: User = Depends(deps.get_current_user), # Changed to get_current_user
    db: Session = Depends(deps.get_db)
):
    """
    Submit a quest for approval (Kid or Parent).
    """
    # 1. Validate task
    task = db.query(FamilyTask).filter(
        FamilyTask.id == task_id,
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_active == True
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or inactive")

    # 2. Check Verification Requirements
    if task.verification_type == VerificationType.REQUIRE_PHOTO and not request.proof_image_url:
         raise HTTPException(status_code=400, detail="Ảnh minh chứng là bắt buộc cho nhiệm vụ này.")

    # 3. Check if already submitted today
    today_start = datetime.combine(date.today(), datetime.min.time())
    existing_log = db.query(TaskLog).filter(
        TaskLog.family_task_id == task.id,
        TaskLog.kid_id == current_user.id,
        TaskLog.created_at >= today_start
    ).order_by(TaskLog.created_at.desc()).first()
    
    # Allow re-submit only if the latest attempt was rejected.
    if existing_log and existing_log.status != TaskStatus.REJECTED:
        raise HTTPException(status_code=400, detail="Task already submitted today")

    # 4. Determine initial status based on VerificationType
    initial_status = TaskStatus.PENDING_APPROVAL
    if task.verification_type == VerificationType.AUTO_APPROVE:
        initial_status = TaskStatus.APPROVED

    # 5. Create Task Log
    try:
        new_log = TaskLog(
            kid_id=current_user.id,
            family_task_id=task.id,
            status=initial_status,
            proof_image_url=request.proof_image_url
        )
        
        if initial_status == TaskStatus.APPROVED:
            new_log.resolved_at = datetime.now()
            
            # Auto-create transaction and update balance
            from app.models.logs_transactions import Transaction, TransactionType
            
            transaction = Transaction(
                kid_id=current_user.id,
                amount=task.points_reward,
                transaction_type=TransactionType.TASK_COMPLETION,
                reference_id=new_log.id, # We don't have ID yet, need to flush
                description=f"Auto-approved: {task.name}"
            )
            db.add(new_log)
            db.flush()
            transaction.reference_id = new_log.id
            db.add(transaction)
            
            current_user.current_coin += task.points_reward
            current_user.total_earned_score += task.points_reward
        else:
             db.add(new_log)

        db.commit()
        db.refresh(new_log)

        # 5b. Generate Notification to Parents if PENDING_APPROVAL
        if initial_status == TaskStatus.PENDING_APPROVAL:
            try:
                from app.models.notifications import Notification, NotificationType
                parents = db.query(User).filter(User.family_id == current_user.family_id, User.role == deps.Role.PARENT).all()
                for p in parents:
                    notif = Notification(
                        user_id=p.id,
                        type=NotificationType.SYSTEM,
                        title="Nhiệm vụ mới chờ duyệt",
                        content=f"{current_user.display_name} vừa nộp báo cáo '{task.name}'. Hãy kiểm tra nhé!",
                        reference_id=str(new_log.id),
                        action_data={"tab": "pending"}
                    )
                    db.add(notif)
                db.commit()
            except Exception as e:
                import logging
                logging.error(f"Failed to send notification for task submission: {e}")

        # 6. Audit Log
        AuditService.log(
            db=db,
            action="SUBMIT_QUEST",
            resource_type="TaskLog",
            resource_id=str(new_log.id),
            status=AuditStatus.SUCCESS,
            details={"task_name": task.name, "auto_approved": initial_status == TaskStatus.APPROVED}
        )
        
        return quest_schemas.QuestItem(
            id=new_log.id,
            task_id=task.id,
            name=task.name,
            points_reward=task.points_reward,
            status=new_log.status,
            proof_image_url=new_log.proof_image_url,
            created_at=new_log.created_at,
            verification_type=task.verification_type.value
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
    kid = db.query(User).get(log.kid_id) # Technically this is the user who submitted it (Parent or Kid)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized for this submission")

    if log.status != TaskStatus.PENDING_APPROVAL:
         raise HTTPException(status_code=400, detail="Submission already processed")

    # 2. Process Approval/Rejection
    try:
        log.resolved_at = datetime.now()
        task = db.query(FamilyTask).get(log.family_task_id)
        from app.models.notifications import Notification, NotificationType
        
        if request.action == "APPROVE":
            log.status = TaskStatus.APPROVED
            log.parent_comment = request.comment # Save praise
            
            # Transaction: Add Coin & XP
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
            
            # Notification to Kid
            kid_notif = Notification(
                user_id=kid.id,
                type=NotificationType.SYSTEM,
                title="Tuyệt vời quá! 🎉",
                content=f"Bố/mẹ đã chấm điểm '{task.name}'. Lời khen: {request.comment}",
                reference_id=str(log.id),
                action_data={
                    "tab": "quests", 
                    "show_praise_modal": True, 
                    "task_id": str(task.id), 
                    "points_awarded": points, 
                    "parent_comment": request.comment, 
                    "status": "APPROVED",
                    "task_name": task.name
                }
            )
            db.add(kid_notif)
            
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
            log.parent_comment = request.comment # Save reject reason
            
            kid_notif = Notification(
                user_id=kid.id,
                type=NotificationType.SYSTEM,
                title="Cần cố gắng thêm! 💪",
                content=f"Bố/mẹ chưa duyệt '{task.name}'. Lời nhắn: {request.comment}",
                reference_id=str(log.id),
                action_data={
                    "tab": "quests", 
                    "show_praise_modal": True, 
                    "task_id": str(task.id), 
                    "parent_comment": request.comment, 
                    "status": "REJECTED",
                    "task_name": task.name
                }
            )
            db.add(kid_notif)
            
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

def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@router.get("/master", response_model=List[quest_schemas.QuestBase])
async def get_master_tasks(
    q: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all master tasks for suggestions with optional search and age prioritization.
    """
    query = db.query(MasterTask)
    if q:
        query = query.filter(MasterTask.name.ilike(f"%{q}%"))
    
    master_tasks = query.all()
    
    # Prioritization logic based on kid's age
    user_age = calculate_age(current_user.birth_date)
    
    if user_age is not None:
        # Sort: tasks within age range first, then by proximity to range
        def sort_key(t):
            if t.min_age <= user_age <= t.max_age:
                return (0, 0) # Top priority
            dist = min(abs(t.min_age - user_age), abs(t.max_age - user_age))
            return (1, dist)
        
        master_tasks.sort(key=sort_key)
    
    return [
        quest_schemas.QuestBase(
            id=t.id,
            name=t.name,
            points_reward=t.suggested_value,
            icon_url=t.icon_url,
            min_age=t.min_age,
            max_age=t.max_age
        ) for t in master_tasks
    ]

@router.post("/pick-master", response_model=dict)
async def pick_master_task(
    request: quest_schemas.QuestProposeRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    KID/PARENT: Pick a master task to be added directly to the family's daily list.
    """
    # 1. Validate master task
    master_task = db.query(MasterTask).get(request.master_task_id)
    if not master_task:
        raise HTTPException(status_code=404, detail="Master task not found")

    # 2. Check if already exists in FamilyTask for this family
    existing_task = db.query(FamilyTask).filter(
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.master_task_id == master_task.id,
        FamilyTask.is_deleted == False
    ).first()
    
    if existing_task:
        if not existing_task.is_active:
            existing_task.is_active = True
            db.commit()
        return {"status": "success", "message": "Nhiệm vụ đã có trong danh sách của con rồi!", "already_exists": True}

    # 3. Create new FamilyTask from Master template
    try:
        new_task = FamilyTask(
            family_id=current_user.family_id,
            master_task_id=master_task.id,
            name=master_task.name,
            points_reward=master_task.suggested_value,
            category=master_task.category,
            verification_type=master_task.verification_type,
            is_active=True
        )
        db.add(new_task)
        db.commit()
        
        # Audit Log
        AuditService.log(
            db=db,
            action="PICK_MASTER_TASK",
            resource_type="FamilyTask",
            resource_id=str(new_task.id),
            status=AuditStatus.SUCCESS,
            details={"task_name": master_task.name, "user": current_user.display_name}
        )
        
        return {"status": "success", "message": f"Đã thêm '{master_task.name}' vào danh sách việc cần làm!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to pick task")
async def propose_master_task(
    request: quest_schemas.QuestProposeRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    KID/PARENT: Propose a master task to be added to the family.
    """
    # 1. Validate master task
    master_task = db.query(MasterTask).get(request.master_task_id)
    if not master_task:
        raise HTTPException(status_code=404, detail="Master task not found")

    # 2. Generate Notification to Parents
    try:
        from app.models.notifications import Notification, NotificationType
        parents = db.query(User).filter(User.family_id == current_user.family_id, User.role == Role.PARENT).all()
        for p in parents:
            notif = Notification(
                user_id=p.id,
                type=NotificationType.SYSTEM,
                title="Bé đề xuất nhiệm vụ mới! ✨",
                content=f"{current_user.display_name} muốn làm việc: '{master_task.name}'. Hãy duyệt thêm cho con nhé!",
                reference_id=str(master_task.id),
                action_data={"tab": "tasks", "action": "ADD_MASTER_TASK", "master_task_id": master_task.id}
            )
            db.add(notif)
        db.commit()

        # Audit Log
        AuditService.log(
            db=db,
            action="PROPOSE_QUEST",
            resource_type="MasterTask",
            resource_id=str(master_task.id),
            status=AuditStatus.SUCCESS,
            details={"task_name": master_task.name, "from": current_user.display_name}
        )
        
        return {"status": "success", "message": "Proposal sent to parents"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to send proposal")

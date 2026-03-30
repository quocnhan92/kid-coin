from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.tasks_rewards import FamilyTask, FamilyReward, MasterTask, MasterReward, Category, VerificationType
from app.models.logs_transactions import TaskLog, TaskStatus, RedemptionLog, RedemptionStatus, Transaction, TransactionType
from app.models.user_family import User, Role
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from uuid import UUID
from app.services.audit import AuditService, AuditStatus
from app.schemas import reward as reward_schemas
from app.models.audit import AuditLog

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
    category: str
    verification_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class KidDetailResponse(BaseModel):
    id: UUID
    display_name: str
    avatar_url: Optional[str]
    current_coin: int
    total_earned_score: int
    birth_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CreateKidRequest(BaseModel):
    display_name: str
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None

class UpdateFamilyRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    extra_info: Optional[str] = None

class FamilyResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    extra_info: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateKidRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None

class CreateAdminRequest(BaseModel):
    display_name: str
    username: str

class CreateTaskRequest(BaseModel):
    name: str
    points_reward: int
    category: Category = Category.OTHER
    verification_type: VerificationType = VerificationType.REQUIRE_PHOTO
    master_task_id: Optional[int] = None

class UpdateTaskRequest(BaseModel):
    name: Optional[str] = None
    points_reward: Optional[int] = None
    category: Optional[Category] = None
    verification_type: Optional[VerificationType] = None
    is_active: Optional[bool] = None

class CreateRewardRequest(BaseModel):
    name: str
    points_cost: int
    stock_limit: Optional[int] = None
    master_reward_id: Optional[int] = None

class UpdateRewardRequest(BaseModel):
    name: Optional[str] = None
    points_cost: Optional[int] = None
    stock_limit: Optional[int] = None
    is_active: Optional[bool] = None

class ApproveTaskRequest(BaseModel):
    action: str  # APPROVE or REJECT
    comment: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    status: str
    resource_type: str
    display_name: Optional[str]
    details: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogPaginatedResponse(BaseModel):
    total: int
    logs: List[AuditLogResponse]

class MasterTaskResponse(BaseModel):
    id: int
    name: str
    icon_url: Optional[str]
    suggested_value: int
    category: str
    verification_type: str

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
        User.role == Role.KID,
        User.is_deleted == False # Added soft delete filter
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

@router.post("/kids", response_model=KidDetailResponse)
async def create_kid(
    request: CreateKidRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Create a new kid in the family.
    """
    try:
        from uuid import uuid4
        avatar = request.avatar_url if request.avatar_url else f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.display_name.replace(' ', '')}"
        new_kid = User(
            id=uuid4(),
            family_id=current_user.family_id,
            role=Role.KID,
            display_name=request.display_name,
            avatar_url=avatar
        )
        db.add(new_kid)
        db.commit()
        db.refresh(new_kid)

        AuditService.log(
            db=db,
            action="CREATE_KID",
            resource_type="User",
            resource_id=str(new_kid.id),
            status=AuditStatus.SUCCESS,
            details={"name": request.display_name}
        )

        return new_kid
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_KID", resource_type="User", error=e)
        raise HTTPException(status_code=500, detail="Could not add kid")

@router.get("/kids/{kid_id}", response_model=KidDetailResponse)
async def get_kid_detail(
    kid_id: UUID,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get detailed information about a specific kid.
    """
    kid = db.query(User).filter(
        User.id == kid_id,
        User.family_id == current_user.family_id,
        User.role == Role.KID,
        User.is_deleted == False
    ).first()

    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")

    return kid

@router.put("/kids/{kid_id}", response_model=KidDetailResponse)
async def update_kid(
    kid_id: UUID,
    request: UpdateKidRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Update a kid's profile (Parent action).
    """
    kid = db.query(User).filter(
        User.id == kid_id,
        User.family_id == current_user.family_id,
        User.role == Role.KID,
        User.is_deleted == False
    ).first()

    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")

    try:
        if request.display_name is not None:
            kid.display_name = request.display_name
        if request.avatar_url:
            kid.avatar_url = request.avatar_url
        if request.birth_date:
            kid.birth_date = request.birth_date
        db.commit()
        db.refresh(kid)

        AuditService.log(
            db=db,
            action="UPDATE_KID_PROFILE",
            resource_type="User",
            resource_id=str(kid.id),
            status=AuditStatus.SUCCESS
        )

        return kid
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="UPDATE_KID_PROFILE", resource_type="User", error=e)
        raise HTTPException(status_code=500, detail="Could not update kid")

@router.delete("/kids/{kid_id}")
async def delete_kid(
    kid_id: UUID,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Soft delete a kid from the family.
    """
    kid = db.query(User).filter(
        User.id == kid_id,
        User.family_id == current_user.family_id,
        User.role == Role.KID,
        User.is_deleted == False
    ).first()

    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")

    try:
        kid.is_deleted = True
        db.commit()

        AuditService.log(
            db=db,
            action="DELETE_KID",
            resource_type="User",
            resource_id=str(kid.id),
            status=AuditStatus.SUCCESS
        )

        return {"status": "success", "message": "Kid deleted"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="DELETE_KID", resource_type="User", error=e)
        raise HTTPException(status_code=500, detail="Could not delete kid")

@router.get("/family", response_model=FamilyResponse)
async def get_family_info(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    from app.models.user_family import Family
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family

@router.put("/family", response_model=FamilyResponse)
async def update_family_info(
    request: UpdateFamilyRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    from app.models.user_family import Family
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    if request.name is not None:
        family.name = request.name
    if request.address is not None:
        family.address = request.address
    if request.extra_info is not None:
        family.extra_info = request.extra_info
        
    db.commit()
    db.refresh(family)
    
    AuditService.log(
        db=db,
        action="UPDATE_FAMILY_INFO",
        resource_type="Family",
        resource_id=str(family.id),
        status=AuditStatus.SUCCESS
    )
    return family

@router.post("/admins")
async def create_admin(
    request: CreateAdminRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Create a new admin (Parent/Grandparent) in the family.
    """
    # Check if username already exists globally (username must be unique)
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.")

    try:
        from uuid import uuid4
        new_admin = User(
            id=uuid4(),
            family_id=current_user.family_id,
            role=Role.PARENT,
            display_name=request.display_name,
            username=request.username,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.display_name.replace(' ', '')}"
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        AuditService.log(
            db=db,
            action="CREATE_ADMIN",
            resource_type="User",
            resource_id=str(new_admin.id),
            status=AuditStatus.SUCCESS,
            details={"name": request.display_name, "username": request.username}
        )

        return {"status": "success", "message": f"Đã tạo tài khoản quản trị cho {request.display_name}"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_ADMIN", resource_type="User", error=e)
        raise HTTPException(status_code=500, detail="Lỗi khi tạo tài khoản quản trị")

@router.post("/tasks", response_model=FamilyTaskResponse)
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Create a new family task.
    """
    try:
        new_task = FamilyTask(
            family_id=current_user.family_id,
            master_task_id=request.master_task_id,
            name=request.name,
            points_reward=request.points_reward,
            category=request.category,
            verification_type=request.verification_type,
            is_active=True
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        AuditService.log(
            db=db,
            action="CREATE_TASK",
            resource_type="FamilyTask",
            resource_id=str(new_task.id),
            status=AuditStatus.SUCCESS,
            details={"task_name": request.name, "points": request.points_reward}
        )

        return new_task
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_TASK", resource_type="FamilyTask", error=e)
        raise HTTPException(status_code=500, detail="Could not create task")

@router.put("/tasks/{task_id}", response_model=FamilyTaskResponse)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Update a family task.
    """
    task = db.query(FamilyTask).filter(
        FamilyTask.id == task_id,
        FamilyTask.family_id == current_user.family_id,
        FamilyTask.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        if request.name is not None:
            task.name = request.name
        if request.points_reward is not None:
            task.points_reward = request.points_reward
        if request.category is not None:
            task.category = request.category
        if request.verification_type is not None:
            task.verification_type = request.verification_type
        if request.is_active is not None:
            task.is_active = request.is_active

        db.commit()
        db.refresh(task)

        AuditService.log(
            db=db,
            action="UPDATE_TASK",
            resource_type="FamilyTask",
            resource_id=str(task.id),
            status=AuditStatus.SUCCESS
        )

        return task
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="UPDATE_TASK", resource_type="FamilyTask", error=e)
        raise HTTPException(status_code=500, detail="Could not update task")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Soft delete a family task.
    """
    task = db.query(FamilyTask).filter(
        FamilyTask.id == task_id,
        FamilyTask.family_id == current_user.family_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        task.is_deleted = True
        db.commit()

        AuditService.log(
            db=db,
            action="DELETE_TASK",
            resource_type="FamilyTask",
            resource_id=str(task.id),
            status=AuditStatus.SUCCESS
        )

        return {"status": "success", "message": "Task deleted"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="DELETE_TASK", resource_type="FamilyTask", error=e)
        raise HTTPException(status_code=500, detail="Could not delete task")

@router.post("/rewards", response_model=dict)
async def create_reward(
    request: CreateRewardRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Create a new family reward.
    """
    try:
        new_reward = FamilyReward(
            family_id=current_user.family_id,
            master_reward_id=request.master_reward_id,
            name=request.name,
            points_cost=request.points_cost,
            stock_limit=request.stock_limit,
            is_active=True
        )
        db.add(new_reward)
        db.commit()
        db.refresh(new_reward)

        AuditService.log(
            db=db,
            action="CREATE_REWARD",
            resource_type="FamilyReward",
            resource_id=str(new_reward.id),
            status=AuditStatus.SUCCESS,
            details={"reward_name": request.name, "cost": request.points_cost}
        )

        return {
            "id": new_reward.id,
            "name": new_reward.name,
            "points_cost": new_reward.points_cost,
            "stock_limit": new_reward.stock_limit,
            "is_active": new_reward.is_active
        }
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_REWARD", resource_type="FamilyReward", error=e)
        raise HTTPException(status_code=500, detail="Could not create reward")

@router.put("/rewards/{reward_id}")
async def update_reward(
    reward_id: UUID,
    request: UpdateRewardRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Update a family reward.
    """
    reward = db.query(FamilyReward).filter(
        FamilyReward.id == reward_id,
        FamilyReward.family_id == current_user.family_id,
        FamilyReward.is_deleted == False
    ).first()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    try:
        if request.name is not None:
            reward.name = request.name
        if request.points_cost is not None:
            reward.points_cost = request.points_cost
        if request.stock_limit is not None:
            reward.stock_limit = request.stock_limit
        if request.is_active is not None:
            reward.is_active = request.is_active

        db.commit()
        db.refresh(reward)

        AuditService.log(
            db=db,
            action="UPDATE_REWARD",
            resource_type="FamilyReward",
            resource_id=str(reward.id),
            status=AuditStatus.SUCCESS
        )

        return {
            "id": reward.id,
            "name": reward.name,
            "points_cost": reward.points_cost,
            "stock_limit": reward.stock_limit,
            "is_active": reward.is_active
        }
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="UPDATE_REWARD", resource_type="FamilyReward", error=e)
        raise HTTPException(status_code=500, detail="Could not update reward")

@router.delete("/rewards/{reward_id}")
async def delete_reward(
    reward_id: UUID,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Soft delete a family reward.
    """
    reward = db.query(FamilyReward).filter(
        FamilyReward.id == reward_id,
        FamilyReward.family_id == current_user.family_id
    ).first()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    try:
        reward.is_deleted = True
        db.commit()

        AuditService.log(
            db=db,
            action="DELETE_REWARD",
            resource_type="FamilyReward",
            resource_id=str(reward.id),
            status=AuditStatus.SUCCESS
        )

        return {"status": "success", "message": "Reward deleted"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="DELETE_REWARD", resource_type="FamilyReward", error=e)
        raise HTTPException(status_code=500, detail="Could not delete reward")

@router.post("/tasks/{log_id}/approve")
async def approve_task(
    log_id: UUID,
    request: ApproveTaskRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Approve or reject a task submission.
    """
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Task submission not found")

    # Verify ownership via kid's family
    kid = db.query(User).get(log.kid_id)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized for this submission")

    if log.status != TaskStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Submission already processed")

    # PREVENT SELF-APPROVAL
    if log.kid_id == current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không thể tự duyệt nhiệm vụ của chính mình!")

    try:
        log.resolved_at = datetime.now()
        log.parent_comment = request.comment # Save praise or reject reason

        if request.action.upper() == "APPROVE":
            log.status = TaskStatus.APPROVED

            # Get task details
            task = db.query(FamilyTask).get(log.family_task_id)
            points = task.points_reward

            # Create transaction
            transaction = Transaction(
                kid_id=kid.id,
                amount=points,
                transaction_type=TransactionType.TASK_COMPLETION,
                reference_id=log.id,
                description=f"Approved: {task.name}"
            )
            db.add(transaction)

            # Update kid's balance
            kid.current_coin += points
            kid.total_earned_score += points

            AuditService.log(
                db=db,
                action="APPROVE_TASK",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS,
                details={"points_awarded": points}
            )

        elif request.action.upper() == "REJECT":
            log.status = TaskStatus.REJECTED
            AuditService.log(
                db=db,
                action="REJECT_TASK",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS
            )

        db.commit()
        return {"status": "success", "action": request.action}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="PROCESS_TASK_SUBMISSION", resource_type="TaskLog", error=e)
        raise HTTPException(status_code=500, detail="Could not process submission")

@router.get("/master-tasks", response_model=List[MasterTaskResponse])
async def get_master_tasks(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all suggested master tasks.
    """
    return db.query(MasterTask).all()

@router.get("/master-rewards", response_model=List[reward_schemas.MasterRewardResponse])
async def get_master_rewards(
    q: Optional[str] = None,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all suggested master rewards.
    """
    query = db.query(MasterReward)
    if q:
        query = query.filter(MasterReward.name.ilike(f"%{q}%"))
    return query.all()

@router.post("/rewards/{redemption_id}/confirm")
async def confirm_reward_delivery(
    redemption_id: UUID,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Confirm that a reward has been delivered to the kid.
    """
    log = db.query(RedemptionLog).filter(RedemptionLog.id == redemption_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Redemption log not found")

    kid = db.query(User).get(log.kid_id)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized for this log")

    if log.status != RedemptionStatus.PENDING_DELIVERY:
        raise HTTPException(status_code=400, detail="Reward already delivered")

    try:
        log.status = RedemptionStatus.DELIVERED
        log.delivered_at = datetime.now()
        db.commit()

        AuditService.log(
            db=db,
            action="DELIVER_REWARD",
            resource_type="RedemptionLog",
            resource_id=str(log.id),
            status=AuditStatus.SUCCESS
        )

        return {"status": "success", "message": "Reward marked as delivered"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="DELIVER_REWARD", resource_type="RedemptionLog", error=e)
        raise HTTPException(status_code=500, detail="Could not confirm delivery")

@router.get("/rewards", response_model=list[dict])
async def get_family_rewards(
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get all rewards for the family.
    """
    rewards = db.query(FamilyReward).filter(
        FamilyReward.family_id == current_user.family_id,
        FamilyReward.is_deleted == False
    ).order_by(FamilyReward.created_at.desc()).all()

    return [
        {
            "id": reward.id,
            "name": reward.name,
            "points_cost": reward.points_cost,
            "stock_limit": reward.stock_limit,
            "is_active": reward.is_active,
            "created_at": reward.created_at
        }
        for reward in rewards
    ]


@router.get("/audit-logs", response_model=AuditLogPaginatedResponse)
async def get_audit_logs(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    Get audit logs for the family with server-side filtering and pagination.
    """
    # Join with User to get only logs related to this family
    query = db.query(AuditLog, User).join(
        User, AuditLog.user_id == User.id
    ).filter(
        User.family_id == current_user.family_id
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (AuditLog.action.ilike(search_term)) |
            (AuditLog.resource_type.ilike(search_term)) |
            (User.display_name.ilike(search_term))
        )

    total_count = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    response_logs = []
    for log, user in logs:
        response_logs.append(AuditLogResponse(
            id=log.id,
            action=log.action,
            status=log.status,
            resource_type=log.resource_type,
            display_name=user.display_name,
            details=log.details,
            created_at=log.created_at
        ))
        
    return {"total": total_count, "logs": response_logs}

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
from app.models.notifications import Notification, NotificationType
from app.models.thinking import TaskBid, ProblemBoard, ProblemSolution, WeeklyReflection, SolutionStatus, ReflectionStatus
from app.schemas import thinking as thinking_schemas
from app.models.social import WallOfFame, FamilyChallenge, ChallengeStatus
from app.models.teen import TeenContract, ContractStatus, ContractCheckin, CheckinStatus, PersonalProject, ProjectMilestoneLog, MilestoneStatus
from app.schemas import social as social_schemas
from app.schemas import teen as teen_schemas
from app.schemas.finance import LoanAccountResponse, CreateLoanRequest
from app.models.finance import LoanAccount, LoanStatus
from app.services import thinking_service, finance_service, social_service, teen_service

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
    master_task_id: int
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
    Get all pending tasks for kids in the parent's family (Family + Club tasks).
    """
    from app.models.club_tasks import ClubTask

    # Use explicit join from TaskLog to ensure correctly scoped results
    pending_logs = db.query(TaskLog, User, FamilyTask, ClubTask).select_from(TaskLog).join(
        User, User.id == TaskLog.kid_id
    ).outerjoin(
        FamilyTask, FamilyTask.id == TaskLog.family_task_id
    ).outerjoin(
        ClubTask, ClubTask.id == TaskLog.club_task_id
    ).filter(
        User.family_id == current_user.family_id,
        TaskLog.status == TaskStatus.PENDING_APPROVAL
    ).order_by(TaskLog.created_at.desc()).all()
    
    response = []
    for log, kid, f_task, c_task in pending_logs:
        task_name = f_task.name if f_task else (c_task.name if c_task else "Nhiệm vụ không xác định")
        points_reward = f_task.points_reward if f_task else (c_task.points_reward if c_task else 0)
        
        response.append(PendingTaskResponse(
            log_id=log.id,
            kid_name=kid.display_name,
            kid_avatar=kid.avatar_url,
            task_name=task_name,
            points_reward=points_reward,
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

        # BUG-01/06 FIX: Resolve task from either family_task_id or club_task_id
        from app.models.club_tasks import ClubTask as ClubTaskModel
        if log.family_task_id:
            task = db.query(FamilyTask).get(log.family_task_id)
        elif log.club_task_id:
            task = db.query(ClubTaskModel).get(log.club_task_id)
        else:
            task = None

        if not task:
            raise HTTPException(status_code=404, detail="Task not found for this log")

        if request.action.upper() == "APPROVE":
            log.status = TaskStatus.APPROVED

            points = task.points_reward

            points = task.points_reward

            # --- FINANCE & GAMIFICATION INTEGRATION ---
            from app.services import streak_service, gamification_service, finance_service
            
            # 1. Update total earned score (XP) - Experience is always full points
            kid.total_earned_score += points
            
            # 2. Process Income (Auto-charity and net coins to balance)
            finance_service.process_income(
                db=db, 
                user=kid, 
                amount=points, 
                description=f"Hoàn thành nhiệm vụ: {task.name}",
                reference_id=str(log.id)
            )

            # 3. Update Streak
            streak_service.update_streak(db, str(kid.id))
            
            # 4. Check Level Up
            new_level_obj = gamification_service.check_level_up(db, kid)
            # Logic: If we want to detect IF it's a NEW level up, we'd need to store current level.
            # For Phase 2, we can just trigger a check. 
            # (Note: In a more advanced version, we'd compare current vs old level)
            
            AuditService.log(
                db=db,
                action="APPROVE_TASK",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS,
                details={"points_awarded": points}
            )

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

        elif request.action.upper() == "REJECT":
            log.status = TaskStatus.REJECTED
            AuditService.log(
                db=db,
                action="REJECT_TASK",
                resource_type="TaskLog",
                resource_id=str(log.id),
                status=AuditStatus.SUCCESS
            )

            # Notification to Kid
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
    tasks = db.query(MasterTask).all()
    return [
        MasterTaskResponse(
            master_task_id=t.id,
            name=t.name,
            icon_url=t.icon_url,
            suggested_value=t.suggested_value,
            category=t.category.value,
            verification_type=t.verification_type.value
        ) for t in tasks
    ]

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
    
    rewards = query.all()
    return [
        reward_schemas.MasterRewardResponse(
            master_reward_id=r.id,
            name=r.name,
            icon_url=r.icon_url,
            suggested_cost=r.suggested_cost,
            min_age=r.min_age,
            max_age=r.max_age
        ) for r in rewards
    ]

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

        # BUG-03 FIX: Notification to Kid — commit was missing
        reward = db.query(FamilyReward).get(log.reward_id)
        kid_notif = Notification(
            user_id=kid.id,
            type=NotificationType.SYSTEM,
            title="Quà đã về! 🎁",
            content=f"Bố/mẹ đã giao cho bạn món quà '{reward.name}'. Bạn đã nhận được chưa?",
            reference_id=str(log.id),
            action_data={"tab": "shop", "show_delivery_modal": True, "reward_name": reward.name}
        )
        db.add(kid_notif)
        db.commit()  # BUG-03 FIX: was missing

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
    # BUG-08 FIX: Use outerjoin to include system audit logs where user_id is NULL
    query = db.query(AuditLog, User).outerjoin(
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

    return AuditLogPaginatedResponse(
        total=total_count,
        items=response_logs
    )

# --- THINKING & EXPANSION MANAGEMENT ---

@router.get("/thinking/bids", response_model=List[thinking_schemas.TaskBidResponse])
async def list_family_bids(
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """List all task bids in the family."""
    return db.query(TaskBid).filter(TaskBid.family_id == current_user.family_id).all()

@router.post("/thinking/bids/{bid_id}/respond")
async def respond_to_bid(
    bid_id: UUID,
    request: thinking_schemas.TaskBidRespondRequest,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent responds to a kid's bid (Accept/Reject/Counter)."""
    bid = thinking_service.process_bid_response(
        db=db, 
        bid_id=bid_id, 
        action=request.action, 
        comment=request.comment, 
        counter_price=request.counter_price
    )
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found or invalid action")
    return {"status": "success", "bid_status": bid.status}

@router.post("/thinking/problems", response_model=thinking_schemas.ProblemBoardResponse)
async def create_problem(
    request: thinking_schemas.ProblemBoardCreate,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent posts a problem to the family board."""
    problem = ProblemBoard(
        family_id=current_user.family_id,
        created_by=current_user.id,
        title=request.title,
        description=request.description,
        reward_coins=request.reward_coins,
        deadline=request.deadline
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem

@router.post("/thinking/solutions/{solution_id}/verify")
async def verify_solution(
    solution_id: UUID,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent verifies a kid's solution and awards coins."""
    solution = db.query(ProblemSolution).get(solution_id)
    if not solution or solution.status != SolutionStatus.DONE:
        raise HTTPException(status_code=404, detail="Solution not found or already verified")
    
    # Check family ownership via board
    board = db.query(ProblemBoard).get(solution.board_id)
    if board.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        solution.status = SolutionStatus.VERIFIED
        kid = db.query(User).get(solution.kid_id)
        
        # Reward via finance service (includes auto-charity)
        finance_service.process_income(
            db=db,
            user=kid,
            amount=board.reward_coins,
            description=f"Giải quyết vấn đề: {board.title}",
            reference_id=str(solution.id)
        )
        
        # Notify kid
        notif = Notification(
            user_id=kid.id,
            type=NotificationType.SYSTEM,
            title="Giải đố thành công! 🧠",
            content=f"Chúc mừng! Lời giải của bạn cho '{board.title}' đã được chấp nhận. Thưởng: {board.reward_coins} Coins.",
            action_data={"problem_id": str(board.id)}
        )
        db.add(notif)
        
        db.commit()
        return {"status": "success", "message": "Solution verified and reward issued"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thinking/reflections", response_model=List[thinking_schemas.WeeklyReflectionResponse])
async def list_reflections(
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """List all submitted reflections in the family."""
    return db.query(WeeklyReflection).join(User).filter(
        User.family_id == current_user.family_id,
        WeeklyReflection.status == ReflectionStatus.SUBMITTED
    ).all()

@router.post("/thinking/reflections/{ref_id}/reward")
async def reward_reflection(
    ref_id: UUID,
    request: thinking_schemas.ReflectionRewardRequest,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent rewards a weekly reflection."""
    ref = db.query(WeeklyReflection).get(ref_id)
    if not ref or ref.status != ReflectionStatus.SUBMITTED:
        raise HTTPException(status_code=404, detail="Reflection not found or not submitted")
    
    kid = db.query(User).get(ref.kid_id)
    if kid.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        ref.status = ReflectionStatus.REWARDED
        ref.bonus_coins = request.bonus_coins
        
        # Reward via finance service
        finance_service.process_income(
            db=db,
            user=kid,
            amount=request.bonus_coins,
            description=f"Thưởng Nhìn lại tuần qua ({ref.week_start})",
            reference_id=str(ref.id)
        )
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- SOCIAL & TEEN MANAGEMENT ---

@router.post("/social/wall", response_model=social_schemas.WallPostResponse)
async def post_to_wall(
    request: social_schemas.WallPostCreate,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent posts an achievement to the family wall."""
    kid = db.query(User).get(request.kid_id)
    if not kid or kid.family_id != current_user.family_id:
        raise HTTPException(status_code=404, detail="Kid not found in your family")
        
    post = WallOfFame(
        family_id=current_user.family_id,
        kid_id=request.kid_id,
        posted_by=current_user.id,
        image_url=request.image_url,
        caption=request.caption
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Notify kid
    notif = Notification(
        user_id=kid.id,
        type=NotificationType.SYSTEM,
        title="Bạn đã được vinh danh! 🎉",
        content=f"Bố/mẹ vừa đăng một bài viết về thành tựu của bạn lên bảng tin gia đình.",
        action_data={"post_id": str(post.id)}
    )
    db.add(notif)
    db.commit()
    
    return social_schemas.WallPostResponse(
        id=post.id,
        kid_id=post.kid_id,
        kid_display_name=kid.display_name,
        kid_avatar_url=kid.avatar_url,
        posted_by_name=current_user.display_name,
        image_url=post.image_url,
        caption=post.caption,
        likes_count=0,
        created_at=post.created_at
    )

@router.post("/social/challenges", response_model=social_schemas.FamilyChallengeResponse)
async def create_family_challenge(
    request: social_schemas.FamilyChallengeCreate,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent creates a new family challenge."""
    challenge = FamilyChallenge(
        family_id=current_user.family_id,
        created_by=current_user.id,
        title=request.title,
        description=request.description,
        target_count=request.target_count,
        duration_days=request.duration_days,
        reward_coins=request.reward_coins,
        start_date=request.start_date,
        end_date=request.end_date,
        status=ChallengeStatus.ACTIVE
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    # Notify all kids in family
    kids = db.query(User).filter(User.family_id == current_user.family_id, User.role == Role.KID).all()
    for kid in kids:
        notif = Notification(
            user_id=kid.id,
            type=NotificationType.SYSTEM,
            title="Thử thách gia đình mới! 🏃‍♂️",
            content=f"Cả nhà cùng tham gia thử thách '{challenge.title}' nhé!",
            action_data={"challenge_id": str(challenge.id)}
        )
        db.add(notif)
    db.commit()

    return social_schemas.FamilyChallengeResponse(
        **challenge.__dict__,
        current_progress=0
    )

@router.put("/kids/{kid_id}/teen-mode")
async def toggle_teen_mode(
    kid_id: UUID,
    request: social_schemas.TeenModeToggleRequest,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Toggle Teen Mode for a specific kid."""
    kid = db.query(User).filter(User.id == kid_id, User.family_id == current_user.family_id).first()
    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")
        
    kid.is_teen_mode = request.is_teen_mode
    db.commit()
    
    # Notify kid
    status_str = "kích hoạt" if request.is_teen_mode else "tắt"
    notif = Notification(
        user_id=kid.id,
        type=NotificationType.SYSTEM,
        title="Chế độ Teen Mode!",
        content=f"Bố/mẹ đã {status_str} chế độ Teen Mode cho tài khoản của bạn.",
        action_data={"is_teen_mode": kid.is_teen_mode}
    )
    db.add(notif)
    db.commit()
    

# --- TEEN MANAGEMENT (PARENT SIDE) ---

@router.get("/teen/contracts", response_model=List[teen_schemas.TeenContractResponse])
async def list_teen_contracts(
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """List all teen contracts in the family."""
    return db.query(TeenContract).filter(TeenContract.family_id == current_user.family_id).all()

@router.post("/teen/contracts/{contract_id}/sign")
async def parent_sign_contract(
    contract_id: UUID,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent signs the contract."""
    contract = db.query(TeenContract).filter(TeenContract.id == contract_id, TeenContract.family_id == current_user.family_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    result = teen_service.sign_contract(db, contract_id, current_user.id)
    return {"status": "success", "contract_status": result.status}

@router.post("/teen/projects", response_model=teen_schemas.PersonalProjectResponse)
async def create_teen_project(
    request: teen_schemas.PersonalProjectCreate,
    kid_id: UUID,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Parent creates a personal project for a teen."""
    kid = db.query(User).filter(User.id == kid_id, User.family_id == current_user.family_id).first()
    if not kid or not kid.is_teen_mode:
        raise HTTPException(status_code=400, detail="Kid not found or NOT in Teen Mode")
        
    project = teen_service.create_project(db, kid_id, current_user.family_id, request.dict())
    return project

@router.post("/teen/projects/{project_id}/milestones/{milestone_idx}/verify")
async def verify_project_milestone(
    project_id: UUID,
    milestone_idx: int,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Verify milestone and release coins."""
    project = db.query(PersonalProject).filter(PersonalProject.id == project_id, PersonalProject.family_id == current_user.family_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Find the pending log for this milestone
    log = db.query(ProjectMilestoneLog).filter(
        ProjectMilestoneLog.project_id == project_id,
        ProjectMilestoneLog.milestone_index == milestone_idx,
        ProjectMilestoneLog.status == MilestoneStatus.PENDING
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Pending milestone submission not found")
        
    # Verify and release coins
    log.status = MilestoneStatus.VERIFIED
    log.verified_by = current_user.id
    
    # Process reward
    kid = db.query(User).get(project.kid_id)
    finance_service.process_income(
        db=db,
        user=kid,
        amount=log.coins_released,
        description=f"Dự án {project.title}: Đạt mốc #{milestone_idx+1}",
        reference_id=log.id
    )
    
    db.commit()
    return {"status": "success", "released_coins": log.coins_released}

# --- FINANCE MANAGEMENT (PARENT SIDE) ---

@router.get("/finance/loans", response_model=List[LoanAccountResponse])
async def list_family_loans(
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """List all loans for kids in the family."""
    return db.query(LoanAccount).filter(LoanAccount.family_id == current_user.family_id).all()

@router.post("/finance/loans", response_model=LoanAccountResponse)
async def create_loan(
    request: CreateLoanRequest,
    current_user: User = Depends(deps.require_role(Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """Create a new loan for a kid in the family."""
    kid = db.query(User).filter(User.id == request.kid_id, User.family_id == current_user.family_id).first()
    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")
        
    loan = LoanAccount(
        kid_id=request.kid_id,
        family_id=current_user.family_id,
        loan_amount=request.loan_amount,
        interest_rate=request.interest_rate,
        total_owed=int(request.loan_amount + (request.loan_amount * request.interest_rate / 100)),
        payment_cycle=request.payment_cycle,
        installments_count=request.installments_count,
        repaid_amount=0,
        due_date=request.due_date,
        status=LoanStatus.ACTIVE,
        approved_by=current_user.id
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    # Notify Kid
    notif = Notification(
        user_id=kid.id,
        type=NotificationType.SYSTEM,
        title="Khoản vay mới! 💳",
        content=f"Bố/mẹ vừa tạo một khoản vay {request.loan_amount} Xu cho bạn.",
        action_data={"loan_id": str(loan.id)}
    )
    db.add(notif)
    db.commit()
    
    return loan

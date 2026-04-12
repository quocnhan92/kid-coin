from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import os

from app.api import deps
from app.models.admin import AdminUser, AdminRole
from app.models.user_family import Family, User
from app.models.tasks_rewards import MasterTask, MasterReward
from app.models.gamification import AvatarItem, UserLevel
from app.models.audit import AuditLog, AuditStatus
from app.models.logs_transactions import TaskLog
from app.schemas import admin as admin_schemas
from app.schemas import master_data as master_schemas
from app.schemas import analytics as analytics_schemas
from app.schemas import gamification as gamification_schemas
from app.services import admin_service, analytics_service
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- HTML ROUTES ---

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard_page(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    # In a real app, we'd check for admin token in cookies
    token = request.cookies.get("admin_token")
    if not token:
        # For this demo/test environment, we might allow bypass or redirect
        # return RedirectResponse("/api/v1/admin/login-page") 
        pass
        
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "active_page": "dashboard"
    })

@router.get("/families", response_class=HTMLResponse)
async def admin_families_page(request: Request):
    return templates.TemplateResponse("admin/families.html", {
        "request": request,
        "active_page": "families"
    })

@router.get("/master-data", response_class=HTMLResponse)
async def admin_master_data_page(request: Request):
    return templates.TemplateResponse("admin/master_data.html", {
        "request": request,
        "active_page": "master_data"
    })

@router.get("/logs", response_class=HTMLResponse)
async def admin_logs_page(request: Request):
    # Create logs template or just reuse dashboard's log section
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "active_page": "logs"
    })

# --- API ENDPOINTS ---

@router.post("/auth/login", response_model=admin_schemas.AdminToken)
async def admin_login(
    payload: admin_schemas.AdminLoginRequest,
    response: Response,
    db: Session = Depends(deps.get_db)
):
    """Admin login endpoint."""
    admin = admin_service.authenticate_admin(db, payload.username, payload.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = admin_service.create_admin_token(admin.id)
    # Set cookie for potential admin panel UI
    response.set_cookie(key="admin_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/me", response_model=admin_schemas.AdminUserResponse)
async def admin_me(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    """Get current admin profile."""
    admin_id = UUID(admin_subject.split(":")[1])
    admin = db.query(AdminUser).get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.get("/families", response_model=List[admin_schemas.FamilyAdminResponse])
async def list_families(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    """List all families (Admin only)."""
    return admin_service.list_families(db)

@router.put("/users/{user_id}/adjust-coins")
async def adjust_user_coins(
    user_id: UUID,
    request: admin_schemas.CoinAdjustmentRequest,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    """Admin adjusts user coins."""
    result = admin_service.adjust_user_coins(
        db=db,
        user_id=request.user_id,
        amount=request.amount,
        reason=request.reason
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "new_balance": result.current_coin}

# --- MASTER DATA CRUD ---

@router.get("/master-tasks", response_model=List[master_schemas.MasterTaskResponse])
async def list_master_tasks(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    return db.query(MasterTask).all()

@router.post("/master-tasks", response_model=master_schemas.MasterTaskResponse)
async def create_master_task(
    request: master_schemas.MasterTaskCreate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    task = MasterTask(**request.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/master-tasks/{task_id}", response_model=master_schemas.MasterTaskResponse)
async def update_master_task(
    task_id: int,
    request: master_schemas.MasterTaskUpdate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    task = db.query(MasterTask).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/master-tasks/{task_id}")
async def delete_master_task(
    task_id: int,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    task = db.query(MasterTask).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"status": "success"}

@router.get("/master-rewards", response_model=List[master_schemas.MasterRewardResponse])
async def list_master_rewards(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    return db.query(MasterReward).all()

@router.post("/master-rewards", response_model=master_schemas.MasterRewardResponse)
async def create_master_reward(
    request: master_schemas.MasterRewardCreate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    reward = MasterReward(**request.dict())
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward

@router.put("/master-rewards/{reward_id}", response_model=master_schemas.MasterRewardResponse)
async def update_master_reward(
    reward_id: int,
    request: master_schemas.MasterRewardUpdate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    reward = db.query(MasterReward).get(reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reward, key, value)
    
    db.commit()
    db.refresh(reward)
    return reward

@router.delete("/master-rewards/{reward_id}")
async def delete_master_reward(
    reward_id: int,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    reward = db.query(MasterReward).get(reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    db.delete(reward)
    db.commit()
    return {"status": "success"}

# --- AVATAR ITEMS CRUD ---

@router.get("/avatar-items", response_model=List[gamification_schemas.AvatarItemResponse])
async def list_avatar_items(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    return db.query(AvatarItem).all()

@router.post("/avatar-items", response_model=gamification_schemas.AvatarItemResponse)
async def create_avatar_item(
    request: gamification_schemas.AvatarItemCreate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    item = AvatarItem(**request.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/avatar-items/{item_id}", response_model=gamification_schemas.AvatarItemResponse)
async def update_avatar_item(
    item_id: int,
    request: gamification_schemas.AvatarItemUpdate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    item = db.query(AvatarItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/avatar-items/{item_id}")
async def delete_avatar_item(
    item_id: int,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    item = db.query(AvatarItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"status": "success"}

# --- USER LEVELS CRUD ---

@router.get("/user-levels", response_model=List[gamification_schemas.UserLevelResponse])
async def list_user_levels(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    return db.query(UserLevel).order_by(UserLevel.level).all()

@router.post("/user-levels", response_model=gamification_schemas.UserLevelResponse)
async def create_user_level(
    request: gamification_schemas.UserLevelCreate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    level = UserLevel(**request.dict())
    db.add(level)
    db.commit()
    db.refresh(level)
    return level

@router.put("/user-levels/{level_id}", response_model=gamification_schemas.UserLevelResponse)
async def update_user_level(
    level_id: int,
    request: gamification_schemas.UserLevelUpdate,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    level = db.query(UserLevel).get(level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(level, key, value)
    
    db.commit()
    db.refresh(level)
    return level

@router.delete("/user-levels/{level_id}")
async def delete_user_level(
    level_id: int,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    level = db.query(UserLevel).get(level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    db.delete(level)
    db.commit()
    return {"status": "success"}

# --- ANALYTICS & STATS ---

@router.get("/analytics/dashboard", response_model=analytics_schemas.AnalyticsDashboardResponse)
async def get_dashboard(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    return {
        "financials": analytics_service.get_financial_summary(db),
        "popular_tasks": analytics_service.get_popular_tasks(db),
        "weekly_activity": analytics_service.get_weekly_activity(db),
        "system_status": analytics_service.get_system_status(db)
    }

@router.get("/stats/daily-active")
async def get_daily_active_stats(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    """Get active users count per day for the last 7 days."""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Simple count based on audit logs activity
    results = db.query(
        func.date(AuditLog.created_at).label("date"),
        func.count(func.distinct(AuditLog.user_id)).label("count")
    ).filter(AuditLog.created_at >= seven_days_ago)\
     .group_by(func.date(AuditLog.created_at))\
     .order_by("date").all()
     
    return [{"date": str(r.date), "count": r.count} for r in results]

@router.get("/logs/errors")
async def get_error_logs(
    limit: int = 20,
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    """Get recent failed operations from audit logs."""
    logs = db.query(AuditLog).filter(AuditLog.status == AuditStatus.FAILED)\
             .order_by(AuditLog.created_at.desc())\
             .limit(limit).all()
    
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "error": log.error_message,
            "resource": f"{log.resource_type}:{log.resource_id}",
            "at": log.created_at
        } for log in logs
    ]

# --- SYSTEM HEALTH ---

@router.get("/system/health")
async def system_health(
    admin_subject: str = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    return {
        "status": "ok",
        "database": db_status,
        "scheduler": "active", # Simplified
        "timestamp": datetime.utcnow()
    }

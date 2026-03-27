from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user_family import User
from app.models.notifications import Notification
from app.schemas.notification import NotificationResponse, NotificationsListResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=NotificationsListResponse)
async def get_my_notifications(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get all notifications for the current user, sorted by newest first.
    Returns both the items and the count of unread notifications.
    """
    notifications = db.query(Notification)\
        .filter(Notification.user_id == current_user.id)\
        .order_by(Notification.created_at.desc())\
        .limit(limit)\
        .all()
        
    unread_count = db.query(Notification)\
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)\
        .count()
        
    return {"unread_count": unread_count, "items": notifications}

@router.put("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Mark a specific notification as read.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    
    return {"status": "success", "message": "Notification marked as read"}

@router.put("/read-all", response_model=dict)
async def mark_all_read(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Mark all unread notifications for the user as read.
    """
    db.query(Notification)\
      .filter(Notification.user_id == current_user.id, Notification.is_read == False)\
      .update({"is_read": True})
      
    db.commit()
    return {"status": "success", "message": "All notifications marked as read"}

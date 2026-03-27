from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from app.models.notifications import NotificationType

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    content: Optional[str] = None
    reference_id: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationsListResponse(BaseModel):
    unread_count: int
    items: list[NotificationResponse]

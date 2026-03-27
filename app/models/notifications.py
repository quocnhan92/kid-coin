from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class NotificationType(str, enum.Enum):
    SYSTEM = "SYSTEM"
    CLUB_INVITE = "CLUB_INVITE"
    KID_CLUB_INVITE = "KID_CLUB_INVITE" # Dành riêng cho PARENT nhận thay KID
    TASK_ASSIGNED = "TASK_ASSIGNED"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    type = Column(Enum(NotificationType), default=NotificationType.SYSTEM, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String(1000), nullable=True)
    
    # ID của resource liên quan (ví dụ: club_id, invitation_id, task_id)
    reference_id = Column(String(36), nullable=True)
    action_data = Column(JSON, nullable=True) # {"invitation_id": "...", "club_name": "..."}
    
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

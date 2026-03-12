from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class AuditStatus(str, enum.Enum):
    INIT = "INIT"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True) # Nullable for system actions or unauthenticated
    action = Column(String(100), nullable=False, index=True) # e.g., 'CREATE_TASK', 'APPROVE_TASK'
    status = Column(Enum(AuditStatus), default=AuditStatus.INIT, nullable=False, index=True)
    
    resource_type = Column(String(50), nullable=False, index=True) # e.g., 'Task', 'User'
    resource_id = Column(String(36), nullable=True, index=True) # ID of the affected resource
    
    request_id = Column(String(50), nullable=True, index=True) # Trace ID to link multiple logs of same request
    details = Column(JSON, nullable=True) # Store input params, changes (diff), etc.
    error_message = Column(String, nullable=True) # Stack trace or error message if FAILED
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=True) # Time taken if applicable
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, status={self.status}, user={self.user_id})>"

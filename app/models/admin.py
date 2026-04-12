from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    MODERATOR = "MODERATOR"
    SUPPORT = "SUPPORT"

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    role = Column(Enum(AdminRole), server_default='MODERATOR', default=AdminRole.MODERATOR)
    is_active = Column(Boolean, server_default='true', default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

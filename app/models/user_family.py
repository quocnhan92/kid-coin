from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime, Index, BigInteger, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class Role(str, enum.Enum):
    PARENT = "PARENT"
    KID = "KID"

class Family(Base):
    __tablename__ = "families"
    __table_args__ = (
        Index("idx_family_name", "name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    extra_info = Column(String(500), nullable=True)
    parent_pin = Column(String(60), nullable=True) # Hashed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="family")
    tasks = relationship("FamilyTask", back_populates="family")
    rewards = relationship("FamilyReward", back_populates="family")
    clubs = relationship("Club", back_populates="creator_family")
    devices = relationship("FamilyDevice", back_populates="family") # Added
    created_club_tasks = relationship("ClubTask", back_populates="creator_family") # Added

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_user_family_role", "family_id", "role"),
        Index("idx_user_username", "username"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    role = Column(Enum(Role), nullable=False)
    username = Column(String(100), unique=True, nullable=True)
    display_name = Column(String(50), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=True) # Added birth_date for age filtering
    current_coin = Column(BigInteger, default=0) # Changed to BigInteger
    total_earned_score = Column(BigInteger, default=0) # Added field, BigInteger
    is_deleted = Column(Boolean, default=False) # Soft delete flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="users")
    logs = relationship("TaskLog", back_populates="kid")
    redemption_logs = relationship("RedemptionLog", back_populates="kid")
    transactions = relationship("Transaction", back_populates="kid")
    club_memberships = relationship("ClubMember", back_populates="user", cascade="all, delete-orphan") # Updated back_populates to user
    audit_logs = relationship("AuditLog", back_populates="user")

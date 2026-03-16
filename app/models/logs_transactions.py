from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Index, BigInteger, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class TaskStatus(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class RedemptionStatus(str, enum.Enum):
    PENDING_DELIVERY = "PENDING_DELIVERY"
    DELIVERED = "DELIVERED"

class TransactionType(str, enum.Enum):
    TASK_COMPLETION = "TASK_COMPLETION"
    REWARD_REDEMPTION = "REWARD_REDEMPTION"
    PENALTY = "PENALTY"
    BONUS = "BONUS"

class TaskLog(Base):
    __tablename__ = "task_logs"
    __table_args__ = (
        Index("idx_task_log_status", "status"),
        Index("idx_task_log_created_at", "created_at"),
        CheckConstraint(
            "num_nonnulls(family_task_id, club_task_id) = 1",
            name="chk_one_task_source"
        )
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Polymorphic relationship: A log belongs to EITHER a family task OR a club task
    family_task_id = Column(UUID(as_uuid=True), ForeignKey("family_tasks.id"), nullable=True, index=True)
    club_task_id = Column(UUID(as_uuid=True), ForeignKey("club_tasks.id"), nullable=True, index=True)
    
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING_APPROVAL)
    proof_image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    kid = relationship("User", back_populates="logs")
    family_task = relationship("FamilyTask", back_populates="logs")
    club_task = relationship("ClubTask", back_populates="logs")

class RedemptionLog(Base):
    __tablename__ = "redemption_logs"
    __table_args__ = (
        Index("idx_redemption_log_status", "status"),
        Index("idx_redemption_log_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reward_id = Column(UUID(as_uuid=True), ForeignKey("family_rewards.id"), nullable=False, index=True)
    status = Column(Enum(RedemptionStatus), default=RedemptionStatus.PENDING_DELIVERY)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    kid = relationship("User", back_populates="redemption_logs")
    reward = relationship("FamilyReward", back_populates="redemption_logs")

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transaction_type", "transaction_type"),
        Index("idx_transaction_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(BigInteger, nullable=False) # Changed to BigInteger
    transaction_type = Column(Enum(TransactionType), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True, index=True) # Could link to TaskLog or Reward redemption
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kid = relationship("User", back_populates="transactions")

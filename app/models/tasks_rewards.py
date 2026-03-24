from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime, Index, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class Category(str, enum.Enum):
    STUDY = "Học tập"
    CHORE = "Việc nhà"
    ENTERTAINMENT = "Giải trí"
    SOCIAL = "Xã hội"
    PERSONAL = "Cá nhân"
    MONEY_MAKING = "Kiếm tiền"
    OTHER = "Khác"

class VerificationType(str, enum.Enum):
    AUTO_APPROVE = "Tự động duyệt"
    REQUIRE_PHOTO = "Cần chụp ảnh"
    REQUIRE_PARENT_CHECK = "Bố mẹ kiểm tra trực tiếp"

class MasterTask(Base):
    __tablename__ = "master_tasks"
    __table_args__ = (
        Index("idx_master_task_category", "category"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    icon_url = Column(String(255), nullable=True)
    suggested_value = Column(BigInteger, default=10)
    category = Column(Enum(Category), nullable=False)
    verification_type = Column(Enum(VerificationType), default=VerificationType.REQUIRE_PHOTO)

    family_tasks = relationship("FamilyTask", back_populates="master_task")

class FamilyTask(Base):
    __tablename__ = "family_tasks"
    __table_args__ = (
        Index("idx_family_task_name", "name"),
        Index("idx_family_task_is_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    master_task_id = Column(Integer, ForeignKey("master_tasks.id"), nullable=True)
    name = Column(String(100), nullable=False)
    points_reward = Column(BigInteger, nullable=False)
    category = Column(Enum(Category), default=Category.OTHER)
    verification_type = Column(Enum(VerificationType), default=VerificationType.REQUIRE_PHOTO)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="tasks")
    master_task = relationship("MasterTask", back_populates="family_tasks")
    logs = relationship("TaskLog", back_populates="family_task")

class MasterReward(Base):
    __tablename__ = "master_rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    icon_url = Column(String(255), nullable=True)
    suggested_cost = Column(BigInteger, default=50)

    family_rewards = relationship("FamilyReward", back_populates="master_reward")

class FamilyReward(Base):
    __tablename__ = "family_rewards"
    __table_args__ = (
        Index("idx_family_reward_name", "name"),
        Index("idx_family_reward_is_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    master_reward_id = Column(Integer, ForeignKey("master_rewards.id"), nullable=True)
    name = Column(String(100), nullable=False)
    points_cost = Column(BigInteger, nullable=False)
    stock_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="rewards")
    master_reward = relationship("MasterReward", back_populates="family_rewards")
    redemption_logs = relationship("RedemptionLog", back_populates="reward")
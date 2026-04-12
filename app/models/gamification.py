from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime, Integer, BigInteger, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class ItemType(str, enum.Enum):
    FRAME = "FRAME"
    BACKGROUND = "BACKGROUND"
    BADGE = "BADGE"
    ACCESSORY = "ACCESSORY"

class UserLevel(Base):
    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    min_xp = Column(BigInteger, nullable=False)
    description = Column(String(500), nullable=True)

class UserStreak(Base):
    __tablename__ = "user_streaks"
    __table_args__ = (
        CheckConstraint('longest_streak >= current_streak', name='chk_streak_longest_gte_current'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    current_streak = Column(Integer, server_default='0', default=0)
    longest_streak = Column(Integer, server_default='0', default=0)
    last_active_date = Column(Date, nullable=True)
    streak_bonus_active = Column(Boolean, server_default='false', default=False)
    streak_frozen_until = Column(Date, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="streak")

class AvatarItem(Base):
    __tablename__ = "avatar_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    image_url = Column(String(255), nullable=False)
    price_coins = Column(Integer, nullable=False)
    min_level = Column(Integer, server_default='1', default=1)
    is_active = Column(Boolean, server_default='true', default=True)

class UserAvatarItem(Base):
    __tablename__ = "user_avatar_items"
    __table_args__ = (
        CheckConstraint('user_id IS NOT NULL', name='chk_user_id_not_null'), # Example, though redundant with nullable=False
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("avatar_items.id"), nullable=False)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    is_equipped = Column(Boolean, server_default='false', default=False)

    user = relationship("User")
    item = relationship("AvatarItem")

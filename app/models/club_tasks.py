from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class ClubTask(Base):
    __tablename__ = "club_tasks"
    __table_args__ = (
        Index("idx_club_task_club_id", "club_id"),
        Index("idx_club_task_is_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    creator_family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    points_reward = Column(BigInteger, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    club = relationship("Club", back_populates="tasks")
    creator_family = relationship("Family", back_populates="created_club_tasks")
    logs = relationship("TaskLog", back_populates="club_task")

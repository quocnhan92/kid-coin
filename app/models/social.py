from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class Club(Base):
    __tablename__ = "clubs"
    __table_args__ = (
        Index("idx_club_name", "name"),
        Index("idx_club_invite_code", "invite_code"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    creator_family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    invite_code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator_family = relationship("Family", back_populates="clubs")
    members = relationship("ClubMember", back_populates="club")

class ClubMember(Base):
    __tablename__ = "club_members"

    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), primary_key=True, index=True)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    club = relationship("Club", back_populates="members")
    kid = relationship("User", back_populates="club_memberships")

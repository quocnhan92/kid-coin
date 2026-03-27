from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


# --- Enums ---

class ClubRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


# --- Models ---

class Club(Base):
    __tablename__ = "clubs"
    __table_args__ = (
        Index("idx_club_name", "name"),
        Index("idx_club_invite_code", "invite_code"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    creator_family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    invite_code = Column(String(20), unique=True, nullable=False)

    # Trạng thái và Xóa mềm
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Dùng cho Soft Delete

    # Relationships
    creator_family = relationship("Family", back_populates="clubs")
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")
    tasks = relationship("ClubTask", back_populates="club")

class ClubMember(Base):
    __tablename__ = "club_members"

    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    role = Column(Enum(ClubRole), default=ClubRole.MEMBER, nullable=False)

    # Tracking thời gian
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")

class ClubInvitation(Base):
    __tablename__ = "club_invitations"
    __table_args__ = (
        # Ngăn chặn spam: Không thể có 2 lời mời cùng trạng thái cho 1 user vào 1 club
        UniqueConstraint("club_id", "invited_user_id", "status", name="uq_club_user_status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)

    # Tracking thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    club = relationship("Club", backref="invitations")
    invited_user = relationship("User", foreign_keys=[invited_user_id])
    inviter = relationship("User", foreign_keys=[inviter_id])
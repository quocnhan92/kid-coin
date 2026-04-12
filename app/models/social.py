import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Index, UniqueConstraint, Integer, BigInteger, Date
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


class ChallengeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


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

class WallOfFame(Base):
    __tablename__ = "wall_of_fame"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    posted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    image_url = Column(String(255), nullable=True)
    caption = Column(String(500), nullable=False)
    task_log_id = Column(UUID(as_uuid=True), ForeignKey("task_logs.id"), nullable=True)
    likes_count = Column(sa.Integer() if 'sa' in locals() else sa.Integer, server_default='0', default=0) # Need to check if sa imported
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family")
    kid = relationship("User", foreign_keys=[kid_id])
    poster = relationship("User", foreign_keys=[posted_by])
    likes = relationship("WallLike", back_populates="post", cascade="all, delete-orphan")

class WallLike(Base):
    __tablename__ = "wall_likes"

    post_id = Column(UUID(as_uuid=True), ForeignKey("wall_of_fame.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    post = relationship("WallOfFame", back_populates="likes")
    user = relationship("User")

class FamilyChallenge(Base):
    __tablename__ = "family_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    target_count = Column(sa.Integer() if 'sa' in locals() else sa.Integer, nullable=False)
    duration_days = Column(sa.Integer() if 'sa' in locals() else sa.Integer, nullable=False)
    reward_coins = Column(sa.BigInteger() if 'sa' in locals() else sa.BigInteger, nullable=False)
    start_date = Column(sa.Date() if 'sa' in locals() else sa.Date, nullable=False)
    end_date = Column(sa.Date() if 'sa' in locals() else sa.Date, nullable=False)
    status = Column(Enum(ChallengeStatus), server_default='ACTIVE', default=ChallengeStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="challenges")
    creator = relationship("User")

class ChallengeProgress(Base):
    __tablename__ = "challenge_progress"
    __table_args__ = (
        UniqueConstraint('challenge_id', 'user_id', 'check_in_date', name='uq_challenge_user_date'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("family_challenges.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    check_in_date = Column(sa.Date() if 'sa' in locals() else sa.Date, nullable=False)
    proof_image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    challenge = relationship("FamilyChallenge")
    user = relationship("User")
from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, BigInteger, Date, CheckConstraint, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class BidStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COUNTERED = "COUNTERED"

class ProblemStatus(str, enum.Enum):
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class SolutionStatus(str, enum.Enum):
    CLAIMED = "CLAIMED"
    DONE = "DONE"
    VERIFIED = "VERIFIED"

class ReflectionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    REWARDED = "REWARDED"

class TaskBid(Base):
    __tablename__ = "task_bids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    proof_image_url = Column(String(255), nullable=True)
    proposed_coins = Column(BigInteger, nullable=False)
    final_coins = Column(BigInteger, nullable=True)
    status = Column(Enum(BidStatus), server_default='PENDING', default=BidStatus.PENDING)
    parent_comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    kid = relationship("User", back_populates="task_bids")
    family = relationship("Family") # Added in migration but not always needed as rel in model, but keeping it

class ProblemBoard(Base):
    __tablename__ = "problem_boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    reward_coins = Column(BigInteger, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ProblemStatus), server_default='OPEN', default=ProblemStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="problem_boards")
    creator = relationship("User", back_populates="created_problem_boards")
    solutions = relationship("ProblemSolution", back_populates="board")

class ProblemSolution(Base):
    __tablename__ = "problem_solutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("problem_boards.id"), nullable=False, index=True)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    task_description = Column(String(200), nullable=False)
    status = Column(Enum(SolutionStatus), server_default='CLAIMED', default=SolutionStatus.CLAIMED)
    proof_image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    board = relationship("ProblemBoard", back_populates="solutions")
    kid = relationship("User", back_populates="problem_solutions")

class WeeklyReflection(Base):
    __tablename__ = "weekly_reflections"
    __table_args__ = (
        CheckConstraint('kid_id IS NOT NULL', name='chk_reflection_kid_id_not_null'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    week_start = Column(Date, nullable=False)
    q1_answer = Column(Text, nullable=True)
    q2_answer = Column(Text, nullable=True)
    q3_answer = Column(Text, nullable=True)
    bonus_coins = Column(Integer, server_default='0', default=0)
    status = Column(Enum(ReflectionStatus), server_default='PENDING', default=ReflectionStatus.PENDING)
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    kid = relationship("User", back_populates="reflections")

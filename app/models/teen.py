from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, BigInteger, Date, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class PeriodType(str, enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class ContractStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    BREACHED = "BREACHED"

class CheckinStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    MISSED = "MISSED"

class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"

class MilestoneStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class TeenContract(Base):
    __tablename__ = "teen_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    period_type = Column(Enum(PeriodType), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    salary_coins = Column(BigInteger, nullable=False)
    milestones = Column(JSON, nullable=True)
    status = Column(Enum(ContractStatus), server_default='DRAFT', default=ContractStatus.DRAFT)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kid = relationship("User", back_populates="teen_contracts")
    family = relationship("Family")
    checkins = relationship("ContractCheckin", back_populates="contract")

class ContractCheckin(Base):
    __tablename__ = "contract_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("teen_contracts.id"), nullable=False, index=True)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    checkin_date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    proof_url = Column(String(255), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(CheckinStatus), server_default='PENDING', default=CheckinStatus.PENDING)

    contract = relationship("TeenContract", back_populates="checkins")
    kid = relationship("User", foreign_keys=[kid_id])
    verifier = relationship("User", foreign_keys=[verified_by])

class PersonalProject(Base):
    __tablename__ = "personal_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_budget = Column(BigInteger, nullable=False)
    milestones = Column(JSON, nullable=False)
    status = Column(Enum(ProjectStatus), server_default='ACTIVE', default=ProjectStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kid = relationship("User", back_populates="personal_projects")
    family = relationship("Family")
    milestone_logs = relationship("ProjectMilestoneLog", back_populates="project")

class ProjectMilestoneLog(Base):
    __tablename__ = "project_milestone_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("personal_projects.id"), nullable=False, index=True)
    milestone_index = Column(Integer, nullable=False)
    proof_url = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    coins_released = Column(BigInteger, nullable=False)
    status = Column(Enum(MilestoneStatus), server_default='PENDING', default=MilestoneStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("PersonalProject", back_populates="milestone_logs")
    verifier = relationship("User")

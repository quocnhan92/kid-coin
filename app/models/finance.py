from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, BigInteger, Date, CheckConstraint, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class GoalStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class SavingsStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MATURED = "MATURED"
    WITHDRAWN = "WITHDRAWN"

class LoanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REPAID = "REPAID"
    OVERDUE = "OVERDUE"

class SavingGoal(Base):
    __tablename__ = "saving_goals"
    __table_args__ = (
        CheckConstraint('current_amount >= 0', name='chk_saving_goal_current_amount_non_negative'),
        CheckConstraint('target_amount > 0', name='chk_saving_goal_target_amount_positive'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(BigInteger, nullable=False)
    current_amount = Column(BigInteger, server_default='0', default=0)
    icon_url = Column(String(255), nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(Enum(GoalStatus), server_default='ACTIVE', default=GoalStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    kid = relationship("User", back_populates="saving_goals")

class SavingsAccount(Base):
    __tablename__ = "savings_accounts"
    __table_args__ = (
        CheckConstraint('principal > 0', name='chk_savings_account_principal_positive'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    principal = Column(BigInteger, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    early_withdraw_penalty = Column(Numeric(5, 2), server_default='50.00', default=50.00)
    status = Column(Enum(SavingsStatus), server_default='ACTIVE', default=SavingsStatus.ACTIVE)
    matured_amount = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kid = relationship("User", back_populates="savings_accounts")

class LoanAccount(Base):
    __tablename__ = "loan_accounts"
    __table_args__ = (
        CheckConstraint('repaid_amount <= total_owed', name='chk_loan_repaid_lte_total_owed'),
        CheckConstraint('loan_amount > 0', name='chk_loan_amount_positive'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    loan_amount = Column(BigInteger, nullable=False)
    interest_rate = Column(Numeric(5, 2), server_default='10.00', default=10.00)
    total_owed = Column(BigInteger, nullable=False)
    repaid_amount = Column(BigInteger, server_default='0', default=0)
    status = Column(Enum(LoanStatus), server_default='ACTIVE', default=LoanStatus.ACTIVE)
    due_date = Column(Date, nullable=True)
    payment_cycle = Column(String(20), server_default='ONE_TIME', default='ONE_TIME')
    installments_count = Column(Integer, server_default='1', default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    kid = relationship("User", foreign_keys=[kid_id], back_populates="loan_accounts")
    family = relationship("Family", back_populates="loan_accounts")
    approver = relationship("User", foreign_keys=[approved_by])

class CharityFund(Base):
    __tablename__ = "charity_fund"
    __table_args__ = (
        CheckConstraint('balance >= 0', name='chk_charity_fund_balance_non_negative'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), unique=True, nullable=False)
    balance = Column(BigInteger, server_default='0', default=0)
    total_donated = Column(BigInteger, server_default='0', default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="charity_fund")
    donations = relationship("CharityDonation", back_populates="fund")

class CharityDonation(Base):
    __tablename__ = "charity_donations"
    __table_args__ = (
        CheckConstraint('amount > 0', name='chk_charity_donation_amount_positive'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fund_id = Column(UUID(as_uuid=True), ForeignKey("charity_fund.id"), nullable=False, index=True)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(BigInteger, nullable=False)
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fund = relationship("CharityFund", back_populates="donations")
    donor = relationship("User")

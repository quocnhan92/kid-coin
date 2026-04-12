from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from app.models.finance import LoanStatus

class CharityFundResponse(BaseModel):
    balance: int
    total_donated: int

class SavingsAccountResponse(BaseModel):
    id: UUID
    account_type: str
    balance: int
    target_amount: Optional[int]
    target_date: Optional[date]
    interest_rate: float
    status: str

    class Config:
        from_attributes = True

class CreateLoanRequest(BaseModel):
    kid_id: UUID
    loan_amount: int
    interest_rate: float = 0.0
    due_date: Optional[date] = None
    payment_cycle: str = 'ONE_TIME'
    installments_count: int = 1

class LoanAccountResponse(BaseModel):
    id: UUID
    kid_id: UUID
    loan_amount: int
    interest_rate: float
    total_owed: int
    repaid_amount: int
    due_date: Optional[date]
    payment_cycle: str
    installments_count: int
    status: LoanStatus
    created_at: datetime

    class Config:
        from_attributes = True

class FinanceStatusResponse(BaseModel):
    current_coin: int
    total_earned_score: int
    charity_balance: int
    total_savings: int
    total_loans_owed: int

class RepayLoanRequest(BaseModel):
    loan_id: UUID
    amount: int

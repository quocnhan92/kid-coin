from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID

from app.api import deps
from app.models.user_family import User, Role
from app.models.finance import CharityFund, SavingsAccount, LoanAccount, LoanStatus
from app.schemas.finance import FinanceStatusResponse, SavingsAccountResponse, LoanAccountResponse, RepayLoanRequest, CharityFundResponse
from app.services import finance_service

router = APIRouter()

@router.get("/status", response_model=FinanceStatusResponse)
async def get_finance_status(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get overview of kid's financial status."""
    charity_fund = db.query(CharityFund).filter(CharityFund.family_id == current_user.family_id).first()
    charity_balance = charity_fund.balance if charity_fund else 0
    
    total_savings = db.query(func.sum(SavingsAccount.principal)).filter(
        SavingsAccount.kid_id == current_user.id,
        SavingsAccount.status == 'ACTIVE'
    ).scalar() or 0
    
    total_loans = db.query(func.sum(LoanAccount.total_owed - LoanAccount.repaid_amount)).filter(
        LoanAccount.kid_id == current_user.id,
        LoanAccount.status == LoanStatus.ACTIVE
    ).scalar() or 0
    
    return FinanceStatusResponse(
        current_coin=current_user.current_coin,
        total_earned_score=current_user.total_earned_score,
        charity_balance=charity_balance,
        total_savings=total_savings,
        total_loans_owed=total_loans
    )

@router.get("/savings", response_model=List[SavingsAccountResponse])
async def list_savings(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List all savings accounts/goals for the kid."""
    return db.query(SavingsAccount).filter(SavingsAccount.kid_id == current_user.id).all()

@router.get("/loans", response_model=List[LoanAccountResponse])
async def list_loans(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List all loans for the kid."""
    return db.query(LoanAccount).filter(LoanAccount.kid_id == current_user.id).all()

@router.post("/loans/repay")
async def repay_loan(
    request: RepayLoanRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Repay a loan."""
    try:
        loan = finance_service.repay_loan(db, current_user, str(request.loan_id), request.amount)
        return {"status": "success", "remaining_owed": loan.total_owed - loan.repaid_amount}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/charity", response_model=CharityFundResponse)
async def get_charity_fund(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get family charity fund info."""
    fund = db.query(CharityFund).filter(CharityFund.family_id == current_user.family_id).first()
    if not fund:
        return CharityFundResponse(balance=0, total_donated=0)
    return fund

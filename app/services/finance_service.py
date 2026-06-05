from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
import logging

from app.models.user_family import User, Family
from app.models.finance import CharityFund, CharityDonation, SavingGoal, SavingsAccount, LoanAccount, LoanStatus
from app.models.logs_transactions import Transaction, TransactionType
from app.services import coin_ledger_service as ledger

logger = logging.getLogger(__name__)

def process_income(db: Session, user: User, amount: int, description: str, reference_id: Optional[str] = None):
    """
    Processes income for a kid, applying auto-charity deduction if configured.
    """
    # Convert string reference_id to UUID if needed
    ref_uuid = reference_id
    if isinstance(reference_id, str):
        try:
            from uuid import UUID
            ref_uuid = UUID(reference_id)
        except ValueError:
            ref_uuid = None
    # 1. Get Charity Rate (Default to 5% if not set)
    # Using decimal for precise calculation
    charity_rate = Decimal(str(user.charity_rate if user.charity_rate is not None else 5.00))
    
    charity_amount = int((Decimal(amount) * charity_rate / Decimal(100)).to_integral_value())
    net_income = amount - charity_amount

    ledger.credit(
        db,
        user,
        net_income,
        TransactionType.TASK_COMPLETION,
        description,
        reference_id=ref_uuid,
    )
    
    # 3. Handle Charity Fund
    if charity_amount > 0:
        fund = db.query(CharityFund).filter(CharityFund.family_id == user.family_id).first()
        if not fund:
            fund = CharityFund(family_id=user.family_id, balance=0, total_donated=0)
            db.add(fund)
            db.flush()
        
        fund.balance += charity_amount
        
        # Log Charity Transaction
        charity_tx = Transaction(
            kid_id=user.id,
            amount=charity_amount,
            transaction_type=TransactionType.CHARITY_DONATE,
            description=f"Auto-charity from: {description}",
            reference_id=ref_uuid
        )
        db.add(charity_tx)
        
        # Create Charity Donation record
        donation = CharityDonation(
            fund_id=fund.id,
            donor_id=user.id,
            amount=charity_amount,
            message=f"Trích tự động từ nhiệm vụ: {description}"
        )
        db.add(donation)
    
    # 4. Log Income Transaction — net already recorded by ledger.credit
    logger.info(f"Processed income for user {user.id}: Total {amount}, Charity {charity_amount}, Net {net_income}")
    return {"net_income": net_income, "charity_amount": charity_amount}

def repay_loan(db: Session, user: User, loan_id: str, amount: int):
    """
    Repays a loan using kid's current coins.
    """
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id, LoanAccount.kid_id == user.id).first()
    if not loan:
        raise ValueError("Loan not found")
    
    if user.current_coin < amount:
        raise ValueError("Insufficient coins for repayment")

    actual_repay = min(amount, loan.total_owed - loan.repaid_amount)

    ledger.debit(
        db,
        user,
        actual_repay,
        TransactionType.LOAN_REPAY,
        f"Repayment for loan: {loan_id}",
        reference_id=loan.id,
    )
    loan.repaid_amount += actual_repay

    if loan.repaid_amount >= loan.total_owed:
        loan.status = LoanStatus.REPAID

    db.commit()
    return loan

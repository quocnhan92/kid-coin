import sys
import os
sys.path.append(os.getcwd())

from app.models.logs_transactions import Transaction, TransactionType
from app.services import analytics_service

print(f"Transaction class: {Transaction}")
print(f"Transaction attributes: {dir(Transaction)}")
print(f"TransactionType attributes: {dir(TransactionType)}")
print(f"analytics_service location: {analytics_service.__file__}")

try:
    from app.core.database import SessionLocal
    db = SessionLocal()
    analytics_service.get_financial_summary(db)
except Exception as e:
    import traceback
    traceback.print_exc()

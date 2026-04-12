from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.user_family import User, Family
from app.models.logs_transactions import Transaction, TransactionType, TaskLog, TaskStatus
from app.models.finance import CharityFund

def get_financial_summary(db: Session):
    total_earned = db.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == TransactionType.INCOME).scalar() or 0
    total_spent = db.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == TransactionType.EXPENSE).scalar() or 0
    charity_balance = db.query(func.sum(CharityFund.balance)).scalar() or 0
    
    # Simple count of active kids
    active_kids = db.query(User).filter(User.is_deleted == False).count()
    
    return {
        "total_earned": total_earned,
        "total_spent": abs(total_spent),
        "charity_balance": charity_balance,
        "total_active_savings": 0 # Placeholder for agora/savings logic if needed
    }

def get_popular_tasks(db: Session, limit: int = 5):
    from app.models.tasks_rewards import FamilyTask
    results = db.query(
        FamilyTask.name.label("name"),
        func.count(TaskLog.id).label("count"),
        func.sum(FamilyTask.points_reward).label("total_earned")
    ).join(FamilyTask, TaskLog.family_task_id == FamilyTask.id)\
     .filter(TaskLog.status == TaskStatus.APPROVED)\
     .group_by(FamilyTask.name)\
     .order_by(desc("count"))\
     .limit(limit).all()
     
    return [{"name": r.name or "Nhiệm vụ", "count": r.count, "total_earned": r.total_earned} for r in results]

def get_weekly_activity(db: Session):
    # Mocking or querying daily active users (logins in last 7 days)
    today = datetime.utcnow().date()
    results = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        # Simplified: count users created or having logs on that day
        count = db.query(User).filter(func.date(User.created_at) <= day).count() # Just an example
        results.append({"date": day, "active_users": count})
    return results

def get_system_status(db: Session):
    return {
        "db_connection": "healthy",
        "version": "1.2.0-expansion",
        "uptime_seconds": 3600 # Placeholder
    }

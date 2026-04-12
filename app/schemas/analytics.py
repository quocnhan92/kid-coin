from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class FinancialSummary(BaseModel):
    total_earned: int
    total_spent: int
    charity_balance: int
    total_active_savings: int

class PopularTask(BaseModel):
    name: str
    count: int
    total_earned: int

class UserActivity(BaseModel):
    date: date
    active_users: int

class AnalyticsDashboardResponse(BaseModel):
    financials: FinancialSummary
    popular_tasks: List[PopularTask]
    weekly_activity: List[UserActivity]
    system_status: Dict[str, Any]

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_family import User
from app.services.audit import AuditService

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    # Example Audit Log
    AuditService.log(
        db=db,
        user_id=None, # In a real scenario, get the current user ID
        action="VIEW_ALL_USERS",
        resource_type="User",
        details={"count": len(users)},
        ip_address="127.0.0.1"
    )
    return users

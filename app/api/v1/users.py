from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_family import User
from app.api import deps
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/me")
def get_me(current_user: User = Depends(deps.get_current_user)):
    return {
        "id": current_user.id,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
        "current_coin": current_user.current_coin,
        "total_earned_score": current_user.total_earned_score,
        "role": current_user.role
    }

@router.put("/me")
def update_me(
    request: UpdateProfileRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    if request.display_name:
        current_user.display_name = request.display_name
    if request.avatar_url:
        current_user.avatar_url = request.avatar_url
        
    db.commit()
    db.refresh(current_user)
    
    return {
        "status": "success",
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url
    }

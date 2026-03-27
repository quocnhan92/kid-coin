from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.models.user_family import User
from app.api import deps
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

@router.get("/")
def get_users(db: Session = Depends(deps.get_db)):
    users = db.query(User).all()
    return users

@router.get("/search")
def search_users(
    q: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Search for other parent users by display_name or username to invite them to clubs.
    """
    from sqlalchemy import or_
    
    users = db.query(User).filter(
        User.role == deps.Role.PARENT,
        User.id != current_user.id,
        or_(
            User.display_name.ilike(f"%{q}%"),
            User.username.ilike(f"%{q}%")
        )
    ).limit(20).all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "avatar_url": u.avatar_url,
            "role": u.role
        } for u in users
    ]

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
    db: Session = Depends(deps.get_db) # Fix: Use deps.get_db to share the same session
):
    try:
        if request.display_name is not None:
            current_user.display_name = request.display_name
        if request.avatar_url is not None:
            current_user.avatar_url = request.avatar_url
            
        db.add(current_user) # Ensure the object is recognized by the session if detached
        db.commit()
        db.refresh(current_user)
        
        return {
            "status": "success",
            "display_name": current_user.display_name,
            "avatar_url": current_user.avatar_url
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

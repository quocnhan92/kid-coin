from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.api import deps
from app.models.user_family import User, Role
from app.models.social import WallOfFame, WallLike, FamilyChallenge, ChallengeProgress, ChallengeStatus
from app.schemas.social import WallPostResponse, FamilyChallengeResponse, ChallengeCheckInRequest
from app.services import social_service

router = APIRouter()

# --- Wall of Fame ---
@router.get("/wall", response_model=List[WallPostResponse])
async def get_family_wall(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """View the family achievement wall."""
    posts = db.query(WallOfFame, User).join(
        User, WallOfFame.kid_id == User.id
    ).filter(WallOfFame.family_id == current_user.family_id).order_by(WallOfFame.created_at.desc()).all()
    
    # Check if user liked each post
    liked_post_ids = [l.post_id for l in db.query(WallLike.post_id).filter(WallLike.user_id == current_user.id).all()]
    
    response = []
    for post, kid in posts:
        # Get poster name
        poster = db.query(User.display_name).filter(User.id == post.posted_by).scalar()
        
        response.append(
            WallPostResponse(
                id=post.id,
                kid_id=post.kid_id,
                kid_display_name=kid.display_name,
                kid_avatar_url=kid.avatar_url,
                posted_by_name=poster or "Hệ thống",
                image_url=post.image_url,
                caption=post.caption,
                likes_count=post.likes_count,
                is_liked_by_me=(post.id in liked_post_ids),
                created_at=post.created_at
            )
        )
    return response

@router.post("/wall/{post_id}/like")
async def toggle_like(
    post_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Toggle heart/like on a wall post."""
    result = social_service.toggle_post_like(db, current_user.id, post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result

# --- Family Challenge ---
@router.get("/challenges", response_model=List[FamilyChallengeResponse])
async def list_active_challenges(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List all active/upcoming challenges for the family."""
    challenges = db.query(FamilyChallenge).filter(
        FamilyChallenge.family_id == current_user.family_id,
        FamilyChallenge.status == ChallengeStatus.ACTIVE
    ).all()
    
    response = []
    for chall in challenges:
        # Calculate current total progress
        current_progress = db.query(func.count(ChallengeProgress.id)).filter(
            ChallengeProgress.challenge_id == chall.id
        ).scalar() or 0
        
        response.append(
            FamilyChallengeResponse(
                id=chall.id,
                title=chall.title,
                description=chall.description,
                target_count=chall.target_count,
                duration_days=chall.duration_days,
                reward_coins=chall.reward_coins,
                start_date=chall.start_date,
                end_date=chall.end_date,
                status=chall.status,
                current_progress=current_progress,
                created_at=chall.created_at
            )
        )
    return response

@router.post("/challenges/{challenge_id}/checkin")
async def challenge_checkin(
    challenge_id: UUID,
    request: ChallengeCheckInRequest,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid checks-in for a family challenge."""
    try:
        result = social_service.check_in_challenge(
            db=db,
            user_id=current_user.id,
            challenge_id=challenge_id,
            proof_url=request.proof_image_url
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

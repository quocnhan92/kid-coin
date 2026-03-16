from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.social import Club, ClubMember
from app.models.user_family import User
from app.services.audit import AuditService, AuditStatus
from app.schemas import club as club_schemas
import secrets

router = APIRouter()

@router.post("/", response_model=club_schemas.Club) # Use the Pydantic schema here
async def create_club(
    request: club_schemas.ClubCreateRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Create a new club.
    """
    try:
        new_club = Club(
            name=request.name,
            creator_family_id=current_user.family_id,
            invite_code=secrets.token_hex(4).upper() # Generate a random 8-char code
        )
        db.add(new_club)
        db.commit()
        db.refresh(new_club)
        
        AuditService.log(
            db=db,
            action="CREATE_CLUB",
            resource_type="Club",
            resource_id=str(new_club.id),
            status=AuditStatus.SUCCESS
        )
        
        return new_club
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not create club")

@router.post("/join")
async def join_club(
    request: club_schemas.ClubJoinRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Join their kids into a club using an invite code.
    """
    club = db.query(Club).filter(Club.invite_code == request.invite_code.upper()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    # Get all kids from the parent's family
    kids = db.query(User).filter(
        User.family_id == current_user.family_id,
        User.role == deps.Role.KID
    ).all()
    
    if not kids:
        raise HTTPException(status_code=400, detail="No kids in this family to join the club")

    try:
        for kid in kids:
            # Check if already a member
            existing_member = db.query(ClubMember).filter(
                ClubMember.club_id == club.id,
                ClubMember.kid_id == kid.id
            ).first()
            
            if not existing_member:
                new_member = ClubMember(club_id=club.id, kid_id=kid.id)
                db.add(new_member)
        
        db.commit()
        
        AuditService.log(
            db=db,
            action="JOIN_CLUB",
            resource_type="Club",
            resource_id=str(club.id),
            status=AuditStatus.SUCCESS,
            details={"kids_added": [str(k.id) for k in kids]}
        )
        
        return {"status": "success", "message": "Kids have been added to the club"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="JOIN_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not join club")

@router.get("/{club_id}/leaderboard", response_model=club_schemas.Leaderboard)
async def get_leaderboard(
    club_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get the leaderboard for a club, ranked by total earned score.
    """
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    # Check if user is part of the club (either as a member or the creator's family)
    is_creator = club.creator_family_id == current_user.family_id
    is_member = db.query(ClubMember).filter(
        ClubMember.club_id == club_id,
        ClubMember.kid_id == current_user.id
    ).first()

    if not is_creator and not is_member and current_user.role == deps.Role.KID:
        raise HTTPException(status_code=403, detail="Not a member of this club")

    members = db.query(User).join(ClubMember).filter(
        ClubMember.club_id == club_id
    ).order_by(User.total_earned_score.desc()).all()
    
    return {
        "club_name": club.name,
        "members": members
    }

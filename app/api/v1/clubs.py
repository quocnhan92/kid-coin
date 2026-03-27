from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api import deps
from app.models.social import Club, ClubMember, ClubRole, ClubInvitation, InvitationStatus
from app.models.club_tasks import ClubTask
from app.models.user_family import User
from app.services.audit import AuditService, AuditStatus
from app.schemas import club as club_schemas
import secrets
from typing import List
import re
import logging
from app.models.notifications import Notification, NotificationType

logger = logging.getLogger(__name__)

router = APIRouter()

def generate_readable_code(name: str) -> str:
    # Generate a more readable code like "TEAM-A1B2"
    prefix = re.sub(r'[^A-Z0-9]', '', name.upper())[:4]
    suffix = secrets.token_hex(2).upper()
    return f"{prefix}-{suffix}"

@router.post("/", response_model=club_schemas.ClubResponse)
async def create_club(
    request: club_schemas.ClubCreateRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Create a new club. The creator automatically becomes an admin.
    """
    invite_code = request.custom_invite_code
    if invite_code:
        if db.query(Club).filter(Club.invite_code.is_(invite_code)).first():
            raise HTTPException(status_code=400, detail="Mã mời này đã tồn tại.")
    else:
        invite_code = generate_readable_code(request.name)

    try:
        new_club = Club(
            name=request.name,
            description=request.description,
            creator_family_id=current_user.family_id,
            invite_code=invite_code,
            is_active=request.is_active
        )
        db.add(new_club)
        db.flush() # To get the new_club.id

        # Add creator as the first admin
        creator_membership = ClubMember(
            club_id=new_club.id,
            user_id=current_user.id,
            role=ClubRole.ADMIN
        )
        db.add(creator_membership)
        
        db.commit()
        db.refresh(new_club)
        
        AuditService.log(db=db, action="CREATE_CLUB", resource_type="Club", resource_id=str(new_club.id))
        
        return new_club
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not create club")

@router.get("/me", response_model=List[club_schemas.ClubResponse])
async def get_my_clubs(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get clubs that the user is associated with.
    """
    try:
        if current_user.role == deps.Role.PARENT:
            # Get clubs where any family member (including parent) is a member
            family_member_ids = [
                u.id for u in db.query(User.id).filter(User.family_id == current_user.family_id).all()
            ]
            joined_clubs = db.query(Club).join(ClubMember).filter(
                ClubMember.user_id.in_(family_member_ids),
                Club.is_active.is_(True)
            ).all()
            # dedupe
            return list({club.id: club for club in joined_clubs}.values())
        else:
            # Kid sees only clubs they joined
            joined_clubs = db.query(Club).join(ClubMember).filter(
                ClubMember.user_id == current_user.id,
                Club.is_active == True
            ).all()
            return joined_clubs
    except Exception as e:
        # Log full stack for server-side debugging and return JSON error so FE can parse
        logger.exception("Error in get_my_clubs: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}", response_model=club_schemas.ClubDetailResponse)
async def get_club_detail(
    club_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    club = db.query(Club).get(club_id)
    if not club or not club.is_active:
        raise HTTPException(status_code=404, detail="Club not found")

    tasks = db.query(ClubTask).filter(
        ClubTask.club_id == club_id,
        ClubTask.is_active.is_(True),
        ClubTask.is_deleted.is_(False)
    ).all()
    members = db.query(User.id, User.display_name, User.avatar_url, User.total_earned_score, ClubMember.role, ClubMember.joined_at).join(ClubMember, ClubMember.user_id == User.id).filter(
        ClubMember.club_id == club_id
    ).all()

    if not members:
        raise HTTPException(status_code=404, detail="No members found for this club.")

    members_list = [
        {
            "user_id": member_id,
            "display_name": display_name,
            "avatar_url": avatar_url,
            "total_earned_score": total_earned_score,
            "role": role,
            "joined_at": joined_at
        } for member_id, display_name, avatar_url, total_earned_score, role, joined_at in members
    ]

    return {
        "id": club.id,
        "name": club.name,
        "creator_family_id": club.creator_family_id,
        "invite_code": club.invite_code,
        "is_active": club.is_active,
        "created_at": club.created_at,
        "members": members_list,
        "tasks": tasks
    }

@router.put("/{club_id}", response_model=club_schemas.ClubResponse)
async def update_club(
    club_id: str,
    request: club_schemas.ClubUpdateRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể cập nhật thông tin nhóm")

    try:
        if request.name is not None:
            club.name = request.name
        if request.is_active is not None:
            club.is_active = request.is_active

        db.commit()
        db.refresh(club)

        AuditService.log(
            db=db,
            action="UPDATE_CLUB",
            resource_type="Club",
            resource_id=str(club.id),
            status=AuditStatus.SUCCESS
        )

        return club
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="UPDATE_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not update club")

@router.delete("/{club_id}")
async def delete_club(
    club_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể xóa nhóm")

    try:
        club.is_active = False # Soft delete
        db.commit()

        AuditService.log(
            db=db,
            action="DELETE_CLUB",
            resource_type="Club",
            resource_id=str(club.id),
            status=AuditStatus.SUCCESS
        )

        return {"status": "success", "message": "Club deleted"}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="DELETE_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not delete club")

@router.post("/join")
async def join_club(
    request: club_schemas.ClubJoinRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Selectively join their kids into a club using an invite code.
    """
    club = db.query(Club).filter(Club.invite_code == request.invite_code).first()
    if not club or not club.is_active:
        raise HTTPException(status_code=404, detail="Mã mời không hợp lệ hoặc nhóm đã bị khóa.")

    users_to_add = db.query(User).filter(
        User.id.in_(request.user_ids),
        User.family_id == current_user.family_id
    ).all()
    
    if len(users_to_add) != len(request.user_ids):
        raise HTTPException(status_code=403, detail="Một hoặc nhiều thành viên không thuộc gia đình của bạn.")

    try:
        for user in users_to_add:
            existing = db.query(ClubMember).filter_by(club_id=club.id, user_id=user.id).first()
            if not existing:
                new_member = ClubMember(club_id=club.id, user_id=user.id, role=ClubRole.MEMBER)
                db.add(new_member)
        
        db.commit()
        AuditService.log(db=db, action="JOIN_CLUB", resource_type="Club", resource_id=str(club.id), details={"users_added": [str(u.id) for u in users_to_add]})
        return {"status": "success", "message": f"Đã thêm {len(users_to_add)} thành viên vào nhóm."}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="JOIN_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not join club")

@router.delete("/{club_id}/members/{user_id}")
async def remove_club_member(
    club_id: str,
    user_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Remove a member from a club. If a parent is removed, their children are also removed. If a child is removed, their parent is also removed.
    """
    # Check if current user is an admin of the club
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Only admins can remove members from the club.")

    member_to_remove = db.query(ClubMember).filter_by(club_id=club_id, user_id=user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Member not found in the club.")

    try:
        # Check if the user is a parent or child
        user_to_remove = db.query(User).filter(User.id == user_id).first()
        if not user_to_remove:
            raise HTTPException(status_code=404, detail="User not found.")

        family_members = db.query(User).filter(User.family_id == user_to_remove.family_id).all()

        # Remove all family members if the user is a parent or child
        for member in family_members:
            family_member_to_remove = db.query(ClubMember).filter_by(club_id=club_id, user_id=member.id).first()
            if family_member_to_remove:
                db.delete(family_member_to_remove)

        db.commit()
        AuditService.log(
            db=db,
            action="REMOVE_CLUB_MEMBER",
            resource_type="Club",
            resource_id=club_id,
            details={"removed_user": user_id, "removed_family": [member.id for member in family_members]}
        )
        return {"status": "success", "message": "Member and their family have been removed from the club."}
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="REMOVE_CLUB_MEMBER", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not remove member")

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

    # Check if user's family is part of the club
    family_members = db.query(User.id).filter(User.family_id == current_user.family_id).all()
    family_member_ids = [m[0] for m in family_members]  # Ensure correct unpacking of query result

    is_member = db.query(ClubMember).filter(
        ClubMember.club_id == club_id,
        ClubMember.user_id.in_(family_member_ids)
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this club")

    members = db.query(User, ClubMember.role, ClubMember.joined_at).join(ClubMember).filter(
        ClubMember.club_id == club_id
    ).all()

    return {
        "club_name": club.name,
        "members": [
            {
                "user_id": user.id,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
                "total_earned_score": user.total_earned_score,
                "role": role,
                "user_global_role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "joined_at": joined_at
            } for user, role, joined_at in members
        ]
    }

@router.post("/{club_id}/tasks", response_model=club_schemas.ClubTaskResponse)
async def create_club_task(
    club_id: str,
    request: club_schemas.ClubTaskCreateRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Create a task for a club.
    """
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có quyền tạo nhiệm vụ cho nhóm")

    try:
        new_task = ClubTask(
            club_id=club_id,
            creator_family_id=current_user.family_id,
            name=request.name,
            description=request.description,
            points_reward=request.points_reward,
            due_date=request.due_date,
            is_active=True
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        AuditService.log(
            db=db,
            action="CREATE_CLUB_TASK",
            resource_type="ClubTask",
            resource_id=str(new_task.id),
            status=AuditStatus.SUCCESS
        )

        return new_task
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="CREATE_CLUB_TASK", resource_type="ClubTask", error=e)
        raise HTTPException(status_code=500, detail="Could not create club task")

@router.get("/{club_id}/tasks", response_model=list[club_schemas.ClubTaskResponse])
async def get_club_tasks(
    club_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get all active tasks for a club.
    """
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    tasks = db.query(ClubTask).filter(
        ClubTask.club_id == club_id,
        ClubTask.is_active.is_(True),
        ClubTask.is_deleted.is_(False)
        # ClubTask.is_deleted == False
    ).all()

    return tasks

@router.get("/search", response_model=List[club_schemas.ClubResponse])
async def search_clubs(
    query: str = Query(..., description="Search term for club name or invite code"),
    db: Session = Depends(deps.get_db)
):
    """
    Search for clubs by name or invite code.
    """
    try:
        clubs = db.query(Club).filter(
            Club.is_active.is_(True),
            or_(
                Club.name.ilike(f"%{query}%"),
                Club.invite_code == query
            )
        ).all()
        return clubs
    except Exception as e:
        logger.exception("Error in search_clubs: %s", e)
        raise HTTPException(status_code=500, detail="Could not search for clubs")

@router.post("/{club_id}/invite", response_model=club_schemas.ClubResponse)
async def invite_user_to_club(
    club_id: str,
    request: club_schemas.ClubAddMemberRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Invite a user to join a club. Notifications will be sent to parents.
    """
    club = db.query(Club).get(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Only admins can invite members to the club.")

    # Determine the user to invite
    user_to_invite = None
    if request.user_id:
        user_to_invite = db.query(User).filter(User.id == request.user_id).first()
    elif request.username:
        user_to_invite = db.query(User).filter(User.username == request.username).first()

    if not user_to_invite:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if the user is already a member
    existing_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=user_to_invite.id).first()
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of the club.")

    # Check if an invitation is already pending
    existing_invitation = db.query(ClubInvitation).filter_by(
        club_id=club_id, 
        invited_user_id=user_to_invite.id, 
        status=InvitationStatus.PENDING
    ).first()
    if existing_invitation:
        raise HTTPException(status_code=400, detail="User already has a pending invitation to this club.")

    try:
        # Create an invitation instead of directly adding the user
        new_invitation = ClubInvitation(
            club_id=club_id,
            invited_user_id=user_to_invite.id,
            inviter_id=current_user.id,
            status=InvitationStatus.PENDING
        )
        db.add(new_invitation)
        db.commit()

        # Create Notifications
        if user_to_invite.role == deps.Role.PARENT:
            notif = Notification(
                user_id=user_to_invite.id,
                type=NotificationType.CLUB_INVITE,
                title="Lời mời vào nhóm",
                content=f"Bạn vừa được mời vào nhóm: {club.name}",
                reference_id=str(new_invitation.id),
                action_data={"club_id": str(club.id), "club_name": club.name}
            )
            db.add(notif)
        else:
            # Notify the kid
            kid_notif = Notification(
                user_id=user_to_invite.id,
                type=NotificationType.SYSTEM,
                title="Lời mời vào nhóm",
                content=f"Bạn vừa được mời vào nhóm {club.name}. Hãy chờ Bố Mẹ duyệt nhé!",
                reference_id=str(new_invitation.id),
                action_data={"club_id": str(club.id), "club_name": club.name}
            )
            db.add(kid_notif)
            
            # Notify all parents in the family
            parents = db.query(User).filter(
                User.family_id == user_to_invite.family_id,
                User.role == deps.Role.PARENT
            ).all()
            for p in parents:
                p_notif = Notification(
                    user_id=p.id,
                    type=NotificationType.KID_CLUB_INVITE,
                    title="Yêu cầu duyệt nhóm 📬",
                    content=f"Bé {user_to_invite.display_name} được mời vào nhóm {club.name}.",
                    reference_id=str(new_invitation.id),
                    action_data={
                        "tab": "clubs", 
                        "show_club_approve_modal": True, 
                        "club_id": str(club.id), 
                        "club_name": club.name, 
                        "kid_name": user_to_invite.display_name,
                        "invitation_id": str(new_invitation.id)
                    }
                )
                db.add(p_notif)
                
        db.commit()

        AuditService.log(
            db=db,
            action="INVITE_USER_TO_CLUB",
            resource_type="Club",
            resource_id=club_id,
            details={"invited_user": str(user_to_invite.id), "invitation_id": str(new_invitation.id)}
        )

        return club
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="INVITE_USER_TO_CLUB", resource_type="Club", error=e)
        raise HTTPException(status_code=500, detail="Could not invite user to club")

@router.get("/invitations/me", response_model=List[club_schemas.ClubInvitationResponse])
async def get_my_invitations(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get all pending club invitations for the current user's family or themselves.
    """
    try:
        if current_user.role == deps.Role.PARENT:
            # Get invitations for all family members
            family_member_ids = [
                u.id for u in db.query(User.id).filter(User.family_id == current_user.family_id).all()
            ]
            invitations = db.query(ClubInvitation).filter(
                ClubInvitation.invited_user_id.in_(family_member_ids),
                ClubInvitation.status == InvitationStatus.PENDING
            ).all()
        else:
            invitations = db.query(ClubInvitation).filter(
                ClubInvitation.invited_user_id == current_user.id,
                ClubInvitation.status == InvitationStatus.PENDING
            ).all()
        
        return invitations
    except Exception as e:
        logger.exception("Error in get_my_invitations: %s", e)
        raise HTTPException(status_code=500, detail="Could not fetch invitations")

@router.put("/{club_id}/invitations/{invitation_id}/respond")
async def respond_to_invitation(
    club_id: str,
    invitation_id: str,
    request: club_schemas.InvitationRespondRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Respond to a club invitation (ACCEPT or REJECT).
    """
    invitation = db.query(ClubInvitation).filter(
        ClubInvitation.id == invitation_id,
        ClubInvitation.club_id == club_id,
        ClubInvitation.status == InvitationStatus.PENDING
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")

    # Verify that the current user has permission to respond to this invitation
    invited_user = db.query(User).get(invitation.invited_user_id)
    if not invited_user:
        raise HTTPException(status_code=404, detail="Invited user not found")
        
    if invited_user.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this invitation")

    try:
        if request.action.upper() == "ACCEPT":
            existing_member = db.query(ClubMember).filter_by(club_id=club_id, user_id=invited_user.id).first()
            if not existing_member:
                new_member = ClubMember(
                    club_id=club_id,
                    user_id=invited_user.id,
                    role=ClubRole.MEMBER
                )
                db.add(new_member)
            invitation.status = InvitationStatus.ACCEPTED
        elif request.action.upper() == "REJECT":
            invitation.status = InvitationStatus.REJECTED
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Must be ACCEPT or REJECT.")

        db.commit()
        
        # Create Notification back to Kid
        try:
            club = db.query(Club).get(club_id)
            club_name = club.name if club else "nhóm"
            action_vn = "Duyệt" if request.action.upper() == "ACCEPT" else "Từ chối"
            kid_notif = Notification(
                user_id=invited_user.id,
                type=NotificationType.SYSTEM,
                title="Thay đổi nhóm",
                content=f"Bố/Mẹ đã {action_vn} lời mời tham gia {club_name} của bạn.",
                reference_id=invitation_id,
                action_data={"club_id": club_id}
            )
            db.add(kid_notif)
            db.commit()
        except Exception as ex:
            logger.error(f"Failed to send notification to kid: {ex}")
        AuditService.log(
            db=db,
            action="RESPOND_CLUB_INVITATION",
            resource_type="ClubInvitation",
            resource_id=invitation_id,
            details={"action": request.action.upper(), "invited_user": str(invited_user.id)}
        )
        
        return {"status": "success", "message": f"Invitation {request.action.lower()}ed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        AuditService.log_failed(db=db, action="RESPOND_CLUB_INVITATION", resource_type="ClubInvitation", error=e)
        raise HTTPException(status_code=500, detail="Could not process invitation response")

@router.put("/{club_id}/tasks/{task_id}", response_model=club_schemas.ClubTaskResponse)
async def update_club_task(
    club_id: str,
    task_id: str,
    request: club_schemas.ClubTaskUpdateRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Update a club task.
    """
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể sửa nhiệm vụ nhóm")
        
    task = db.query(ClubTask).filter_by(id=task_id, club_id=club_id, is_deleted=False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if request.name is not None:
        task.name = request.name
    if request.description is not None:
        task.description = request.description
    if request.points_reward is not None:
        task.points_reward = request.points_reward
    if request.due_date is not None:
        task.due_date = request.due_date
    if request.is_active is not None:
        task.is_active = request.is_active
        
    try:
        db.commit()
        db.refresh(task)
        AuditService.log(db=db, action="UPDATE_CLUB_TASK", resource_type="ClubTask", resource_id=task_id)
        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update task")

@router.delete("/{club_id}/tasks/{task_id}")
async def delete_club_task(
    club_id: str,
    task_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Soft delete a club task.
    """
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể xóa nhiệm vụ nhóm")
        
    task = db.query(ClubTask).filter_by(id=task_id, club_id=club_id, is_deleted=False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    try:
        task.is_deleted = True
        db.commit()
        AuditService.log(db=db, action="DELETE_CLUB_TASK", resource_type="ClubTask", resource_id=task_id)
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete task")

@router.post("/{club_id}/request-join")
async def request_join_club(
    club_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    PARENT: Request to join a club.
    """
    club = db.query(Club).get(club_id)
    if not club or not club.is_active:
        raise HTTPException(status_code=404, detail="Club not found")
        
    existing_member = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="Đã là thành viên của nhóm.")
        
    existing_req = db.query(ClubInvitation).filter_by(
        club_id=club_id, 
        invited_user_id=current_user.id, 
        inviter_id=current_user.id, 
        status=InvitationStatus.PENDING
    ).first()
    if existing_req:
         raise HTTPException(status_code=400, detail="Đã gửi yêu cầu trước đó.")
         
    try:
        new_req = ClubInvitation(
            club_id=club_id,
            invited_user_id=current_user.id,
            inviter_id=current_user.id,
            status=InvitationStatus.PENDING
        )
        db.add(new_req)
        db.commit()
        AuditService.log(db=db, action="REQUEST_JOIN_CLUB", resource_type="Club", resource_id=club_id)
        return {"status": "success", "message": "Gửi yêu cầu tham gia thành công."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi.")

@router.get("/{club_id}/join-requests", response_model=List[club_schemas.ClubInvitationResponse])
async def get_join_requests(
    club_id: str,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: View join requests for the club.
    """
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể xem yêu cầu")
        
    requests = db.query(ClubInvitation).filter(
        ClubInvitation.club_id == club_id,
        ClubInvitation.inviter_id == ClubInvitation.invited_user_id,
        ClubInvitation.status == InvitationStatus.PENDING
    ).all()
    return requests

@router.put("/{club_id}/join-requests/{request_id}/respond")
async def respond_to_join_request(
    club_id: str,
    request_id: str,
    request: club_schemas.InvitationRespondRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Accept or Reject a join request.
    """
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có thể duyệt yêu cầu")
        
    join_req = db.query(ClubInvitation).filter(
        ClubInvitation.id == request_id,
        ClubInvitation.club_id == club_id,
        ClubInvitation.inviter_id == ClubInvitation.invited_user_id,
        ClubInvitation.status == InvitationStatus.PENDING
    ).first()
    if not join_req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tìm thấy.")
        
    try:
        if request.action.upper() == "ACCEPT":
            existing = db.query(ClubMember).filter_by(club_id=club_id, user_id=join_req.invited_user_id).first()
            if not existing:
                new_member = ClubMember(club_id=club_id, user_id=join_req.invited_user_id, role=ClubRole.MEMBER)
                db.add(new_member)
            join_req.status = InvitationStatus.ACCEPTED
        else:
             join_req.status = InvitationStatus.REJECTED
             
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Không thể duyệt yêu cầu")

class ChangeRoleRequest(BaseModel):
    new_role: ClubRole

@router.put("/{club_id}/members/{user_id}/role")
async def update_club_user_role(
    club_id: str,
    user_id: str,
    request: ChangeRoleRequest,
    current_user: User = Depends(deps.require_role(deps.Role.PARENT)),
    db: Session = Depends(deps.get_db)
):
    """
    ADMIN: Change a club member's role (MEMBER <-> ADMIN).
    Only PARENTs can be made ADMINs.
    """
    admin_membership = db.query(ClubMember).filter_by(club_id=club_id, user_id=current_user.id, role=ClubRole.ADMIN).first()
    if not admin_membership:
        raise HTTPException(status_code=403, detail="Only admins can manage roles.")
    
    target_member = db.query(ClubMember).filter_by(club_id=club_id, user_id=user_id).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found in this club.")
    
    target_user = db.query(User).get(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if request.new_role == ClubRole.ADMIN and target_user.role != deps.Role.PARENT:
        raise HTTPException(status_code=400, detail="Only parent accounts can be promoted to Admin.")
        
    if target_member.role == request.new_role:
        return {"message": "Role unchanged.", "role": request.new_role.value}
        
    if request.new_role == ClubRole.MEMBER and target_member.role == ClubRole.ADMIN:
        admin_count = db.query(ClubMember).filter_by(club_id=club_id, role=ClubRole.ADMIN).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the last admin of the club.")

    target_member.role = request.new_role
    db.commit()
    
    return {"message": f"Successfully updated role to {request.new_role.value}", "role": request.new_role.value}

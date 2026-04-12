from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
import logging

from app.models.social import WallOfFame, WallLike, FamilyChallenge, ChallengeProgress, ChallengeStatus
from app.models.user_family import User
from app.models.notifications import Notification, NotificationType
from app.services import finance_service

logger = logging.getLogger(__name__)

def toggle_post_like(db: Session, user_id: UUID, post_id: UUID):
    """
    Toggle like on a Wall of Fame post.
    """
    existing_like = db.query(WallLike).filter(
        WallLike.post_id == post_id,
        WallLike.user_id == user_id
    ).first()
    
    post = db.query(WallOfFame).get(post_id)
    if not post:
        return None
        
    if existing_like:
        db.delete(existing_like)
        post.likes_count -= 1
        status = "UNLIKED"
    else:
        new_like = WallLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        post.likes_count += 1
        status = "LIKED"
        
        # Notify the kid if they are the subject of the post
        if post.kid_id != user_id:
            notif = Notification(
                user_id=post.kid_id,
                type=NotificationType.SYSTEM,
                title="Ai đó đã thả tim! ❤️",
                content=f"Bài viết về bạn vừa nhận được một lượt thích mới.",
                action_data={"post_id": str(post_id)}
            )
            db.add(notif)
            
    db.commit()
    return {"status": status, "likes_count": post.likes_count}

def check_in_challenge(db: Session, user_id: UUID, challenge_id: UUID, proof_url: Optional[str] = None):
    """
    Check-in for a family challenge for the current day.
    """
    today = date.today()
    
    # Check if challenge is active
    challenge = db.query(FamilyChallenge).get(challenge_id)
    if not challenge or challenge.status != ChallengeStatus.ACTIVE:
        raise ValueError("Thử thách không tồn tại hoặc đã kết thúc.")
        
    if today < challenge.start_date or today > challenge.end_date:
        raise ValueError("Thử thách chưa bắt đầu hoặc đã quá hạn.")
        
    # Check if already checked in today
    existing = db.query(ChallengeProgress).filter(
        ChallengeProgress.challenge_id == challenge_id,
        ChallengeProgress.user_id == user_id,
        ChallengeProgress.check_in_date == today
    ).first()
    
    if existing:
        raise ValueError("Bạn đã điểm danh thử thách này hôm nay rồi!")
        
    progress = ChallengeProgress(
        challenge_id=challenge_id,
        user_id=user_id,
        check_in_date=today,
        proof_image_url=proof_url
    )
    db.add(progress)
    db.commit()
    
    # Check if challenge completed
    total_checkins = db.query(func.count(ChallengeProgress.id)).filter(
        ChallengeProgress.challenge_id == challenge_id
    ).scalar()
    
    if total_checkins >= challenge.target_count:
        complete_challenge(db, challenge)
        
    return {"status": "success", "current_total": total_checkins}

def complete_challenge(db: Session, challenge: FamilyChallenge):
    """
    Finalize a challenge and reward participants.
    """
    challenge.status = ChallengeStatus.COMPLETED
    
    # Find participants (kids who checked-in at least once)
    participants = db.query(User).join(ChallengeProgress).filter(
        ChallengeProgress.challenge_id == challenge.id
    ).distinct().all()
    
    if not participants:
        return
        
    # Reward each participant (Simplest: shared reward equally or full reward?)
    # Based on implementation plan: Default is reward each active participant.
    for participant in participants:
        finance_service.process_income(
            db=db,
            user=participant,
            amount=challenge.reward_coins,
            description=f"Hoàn thành thử thách gia đình: {challenge.title}",
            reference_id=str(challenge.id)
        )
        
        # Notify
        notif = Notification(
            user_id=participant.id,
            type=NotificationType.SYSTEM,
            title="Thử thách hoàn thành! 🏆",
            content=f"Cả nhà đã cùng nhau vượt qua thử thách '{challenge.title}'! Thưởng: {challenge.reward_coins} Coins.",
            action_data={"challenge_id": str(challenge.id)}
        )
        db.add(notif)
        
    db.commit()

def update_challenge_statuses(db: Session):
    """
    Job to expire challenges that reached their end date.
    """
    today = date.today()
    expired = db.query(FamilyChallenge).filter(
        FamilyChallenge.status == ChallengeStatus.ACTIVE,
        FamilyChallenge.end_date < today
    ).all()
    
    for chall in expired:
        chall.status = ChallengeStatus.EXPIRED
        
    db.commit()
    return len(expired)

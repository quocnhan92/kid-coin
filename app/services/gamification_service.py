from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.gamification import UserLevel
from app.models.user_family import User
from app.models.notifications import Notification, NotificationType
import logging

logger = logging.getLogger(__name__)

def get_level_info(db: Session, user: User):
    """
    Get current level and progress info for a user.
    """
    xp = user.total_earned_score or 0
    
    # Get current level (highest level where user.xp >= min_xp)
    current_level = db.query(UserLevel).filter(
        UserLevel.min_xp <= xp
    ).order_by(UserLevel.level.desc()).first()
    
    if not current_level:
        # Fallback to level 1 if no level found (should not happen with seed data)
        current_level = db.query(UserLevel).filter(UserLevel.level == 1).first()
    
    # Get next level
    next_level = db.query(UserLevel).filter(
        UserLevel.level > (current_level.level if current_level else 0)
    ).order_by(UserLevel.level.asc()).first()
    
    xp_to_next = 0
    progress_percentage = 100
    
    if next_level:
        xp_to_next = next_level.min_xp - xp
        total_xp_for_level = next_level.min_xp - (current_level.min_xp if current_level else 0)
        current_xp_in_level = xp - (current_level.min_xp if current_level else 0)
        progress_percentage = min(100, max(0, (current_xp_in_level / total_xp_for_level) * 100))
        
    return {
        "current_level": current_level.level if current_level else 1,
        "level_name": current_level.name if current_level else "Người mới",
        "current_xp": xp,
        "next_level_xp": next_level.min_xp if next_level else None,
        "xp_to_next_level": xp_to_next if next_level else 0,
        "progress_percentage": progress_percentage
    }

def check_level_up(db: Session, user: User):
    """
    Check if user's current XP qualifies for a new level.
    Called after task approval or score increase.
    """
    xp = user.total_earned_score or 0
    
    # Determine the level they SHOULD be at
    correct_level = db.query(UserLevel).filter(
        UserLevel.min_xp <= xp
    ).order_by(UserLevel.level.desc()).first()
    
    if not correct_level:
        return None

    # Logic: We might want to store 'current_level' in the User model eventually,
    # but for now we can rely on total_earned_score.
    # To detect a 'new' level up, we can check if the XP just passed a threshold.
    # For now, let's assume we call this when XP increases.
    
    # If we want to send a notification, we need to know their PREVIOUS level.
    # Since we don't store previous level, we'll implement a simple threshold check.
    # Better: Add 'current_level' to User model in the next step or query it.
    
    return correct_level

def create_level_up_notification(db: Session, user: User, new_level: int, level_name: str):
    """
    Create a level up notification for the kid.
    """
    notif = Notification(
        user_id=user.id,
        type=NotificationType.SYSTEM,
        title="BẠN ĐÃ LÊN CẤP! 🆙",
        content=f"Chúc mừng! Bạn đã đạt Cấp {new_level}: {level_name}!",
        action_data={
            "show_levelup_animation": True,
            "new_level": new_level,
            "level_name": level_name
        }
    )
    db.add(notif)
    logger.info(f"Level up notification created for user {user.id} (Level {new_level})")

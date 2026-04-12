from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.gamification import UserStreak
from app.models.user_family import User
import logging

logger = logging.getLogger(__name__)

def update_streak(db: Session, user_id: str):
    """
    Updates the streak for a kid when a task is approved.
    """
    today = date.today()
    streak = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    
    if not streak:
        # Create new streak if doesn't exist
        streak = UserStreak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_active_date=today
        )
        db.add(streak)
        logger.info(f"Initial streak created for user {user_id}")
    else:
        # If already active today, do nothing
        if streak.last_active_date == today:
            return streak
        
        # If active yesterday, increment streak
        yesterday = today - timedelta(days=1)
        if streak.last_active_date == yesterday:
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            streak.last_active_date = today
            logger.info(f"Streak incremented for user {user_id} to {streak.current_streak}")
        else:
            # Streak broken, reset to 1
            streak.current_streak = 1
            streak.last_active_date = today
            logger.info(f"Streak reset for user {user_id} (last active was {streak.last_active_date})")
    
    db.commit()
    return streak

def reset_expired_streaks(db: Session):
    """
    Cron job logic to reset streaks that have expired (no activity for > 1 day).
    Should be called daily at 00:05.
    """
    yesterday = date.today() - timedelta(days=1)
    
    # Streaks that were NOT active yesterday and NOT active today (yet)
    # are definitely broken.
    expired_streaks = db.query(UserStreak).filter(
        UserStreak.last_active_date < yesterday,
        UserStreak.current_streak > 0
    ).all()
    
    count = 0
    for streak in expired_streaks:
        streak.current_streak = 0
        count += 1
        
    if count > 0:
        db.commit()
        logger.info(f"Reset {count} expired streaks.")
    
    return count

from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
import logging

from app.models.thinking import TaskBid, BidStatus, ProblemBoard, ProblemSolution, SolutionStatus, WeeklyReflection, ReflectionStatus
from app.models.user_family import User, Role
from app.models.notifications import Notification, NotificationType

logger = logging.getLogger(__name__)

def create_weekly_reflections(db: Session):
    """
    Cron job to create a new reflection draft for every kid each Sunday.
    """
    today = date.today()
    # Get all active kids
    kids = db.query(User).filter(User.role == Role.KID, User.is_deleted == False).all()
    
    count = 0
    for kid in kids:
        # Check if already exists for this week
        existing = db.query(WeeklyReflection).filter(
            WeeklyReflection.kid_id == kid.id,
            WeeklyReflection.week_start == today
        ).first()
        
        if not existing:
            reflection = WeeklyReflection(
                kid_id=kid.id,
                week_start=today,
                status=ReflectionStatus.PENDING
            )
            db.add(reflection)
            count += 1
            
            # Notify kid
            notif = Notification(
                user_id=kid.id,
                type=NotificationType.SYSTEM,
                title="Thời gian nhìn lại! 🤔",
                content="Hãy dành ít phút để nhìn lại kết quả tuần qua và đặt mục tiêu tuần mới nhé!",
                action_data={"tab": "reflections", "reflection_date": str(today)}
            )
            db.add(notif)
            
    db.commit()
    logger.info(f"Created {count} weekly reflections for date {today}")
    return count

def process_bid_response(db: Session, bid_id: UUID, action: str, comment: Optional[str] = None, counter_price: Optional[int] = None):
    """
    Parent responds to a kid's task bid.
    """
    bid = db.query(TaskBid).filter(TaskBid.id == bid_id).first()
    if not bid:
        return None
        
    bid.parent_comment = comment
    bid.resolved_at = datetime.now()
    
    if action.upper() == "ACCEPT":
        bid.status = BidStatus.ACCEPTED
        bid.final_coins = bid.proposed_coins
        title = "Đồng ý thương lượng! ✅"
        content = f"Bố/mẹ đã đồng ý mức giá {bid.proposed_coins} cho: {bid.title}"
    elif action.upper() == "REJECT":
        bid.status = BidStatus.REJECTED
        title = "Chưa thể đồng ý! ❌"
        content = f"Bố/mẹ từ chối mức giá đề xuất cho: {bid.title}. Nhắn nhủ: {comment}"
    elif action.upper() == "COUNTER":
        bid.status = BidStatus.COUNTERED
        bid.final_coins = counter_price
        title = "Mức giá mới! 🤝"
        content = f"Bố/mẹ đề xuất mức giá mới ({counter_price}) cho: {bid.title}. Lời nhắn: {comment}"
    else:
        return None
        
    # Notify kid
    notif = Notification(
        user_id=bid.id,
        user_id_rel=bid.kid_id, # Error in model rel usage? Fixed in call below
        type=NotificationType.SYSTEM,
        title=title,
        content=content,
        action_data={"bid_id": str(bid.id), "status": bid.status}
    )
    # Correcting user_id
    notif.user_id = bid.kid_id
    db.add(notif)
    db.commit()
    return bid

def expire_problems(db: Session):
    """
    Job to close expired problems on the board.
    """
    now = datetime.now()
    expired = db.query(ProblemBoard).filter(
        ProblemBoard.status == "OPEN",
        ProblemBoard.deadline < now
    ).all()
    
    for prob in expired:
        prob.status = "EXPIRED"
        
    db.commit()
    return len(expired)

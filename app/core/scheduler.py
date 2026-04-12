import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Jobs Placeholder functions
# Logic for these will be implemented in subsequent phases

def streak_updater_job():
    """Daily job to check and update user streaks."""
    logger.info("Running job: streak_updater_job")
    db = SessionLocal()
    try:
        from app.services import streak_service
        reset_count = streak_service.reset_expired_streaks(db)
        logger.info(f"Streak updater job completed. Reset {reset_count} streaks.")
    finally:
        db.close()

def savings_maturity_job():
    """Daily job to process matured savings goals."""
    logger.info("Running job: savings_maturity_job")
    db = SessionLocal()
    try:
        # TODO: Implement logic in Phase 3
        pass
    finally:
        db.close()

def loan_overdue_job():
    """Daily job to check for overdue loans."""
    logger.info("Running job: loan_overdue_job")
    db = SessionLocal()
    try:
        # TODO: Implement logic in Phase 3
        pass
    finally:
        db.close()

def weekly_reflection_creator_job():
    """Weekly job to create reflection entries for next week."""
    logger.info("Running job: weekly_reflection_creator_job")
    db = SessionLocal()
    try:
        from app.services import thinking_service
        count = thinking_service.create_weekly_reflections(db)
        logger.info(f"Reflection creator job completed. Created {count} records.")
    finally:
        db.close()

def maintenance_cleanup_job():
    """Daily job for expiring challenges and problem boards."""
    logger.info("Running job: maintenance_cleanup_job")
    db = SessionLocal()
    try:
        from app.services import thinking_service, social_service
        # Expire challenges (Phase 5)
        expired_challenges = social_service.update_challenge_statuses(db)
        logger.info(f"Maintenance cleanup: Expired {expired_challenges} challenges.")
        
        # Expire problem boards (Phase 4)
        expired_count = thinking_service.expire_problems(db)
        logger.info(f"Maintenance cleanup: Closed {expired_count} expired problems.")
    finally:
        db.close()

# Initialize Scheduler
scheduler = BackgroundScheduler()

def start_scheduler():
    """Initialize and start the background scheduler."""
    if not scheduler.running:
        # 1. Streak updater: 00:05 AM every day
        scheduler.add_job(streak_updater_job, CronTrigger(hour=0, minute=5), id="streak_updater")
        
        # 2. Finance jobs: 08:00 AM every day
        scheduler.add_job(savings_maturity_job, CronTrigger(hour=8, minute=0), id="savings_maturity")
        scheduler.add_job(loan_overdue_job, CronTrigger(hour=8, minute=5), id="loan_overdue")
        
        # 3. Reflection: 20:00 PM every Sunday
        scheduler.add_job(weekly_reflection_creator_job, CronTrigger(day_of_week='sun', hour=20, minute=0), id="weekly_reflection")
        
        # 4. Cleanup: 23:55 PM every day
        scheduler.add_job(maintenance_cleanup_job, CronTrigger(hour=23, minute=55), id="maintenance_cleanup")
        
        scheduler.start()
        logger.info("Background Scheduler started.")

def shutdown_scheduler():
    """Shutdown the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background Scheduler shutdown.")

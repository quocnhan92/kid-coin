from sqlalchemy import inspect, text
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """
    A simple migration script to add columns if they don't exist,
    avoiding the need to drop the database on every schema change.
    """
    logger.info("Running custom DB migrations...")
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check users table for total_earned_score
        if inspector.has_table("users"):
            columns = [col['name'] for col in inspector.get_columns("users")]
            if "total_earned_score" not in columns:
                logger.info("Adding 'total_earned_score' to 'users' table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN total_earned_score BIGINT DEFAULT 0"))
                conn.commit()

        # Check family_tasks table for category and verification_type
        if inspector.has_table("family_tasks"):
            columns = [col['name'] for col in inspector.get_columns("family_tasks")]
            if "category" not in columns:
                logger.info("Adding 'category' to 'family_tasks' table...")
                conn.execute(text("ALTER TABLE family_tasks ADD COLUMN category VARCHAR(50) DEFAULT 'Khác'"))
                conn.commit()
            if "verification_type" not in columns:
                logger.info("Adding 'verification_type' to 'family_tasks' table...")
                conn.execute(text("ALTER TABLE family_tasks ADD COLUMN verification_type VARCHAR(50) DEFAULT 'Cần chụp ảnh'"))
                conn.commit()

        # Check master_tasks table
        if inspector.has_table("master_tasks"):
            columns = [col['name'] for col in inspector.get_columns("master_tasks")]
            if "verification_type" not in columns:
                logger.info("Adding 'verification_type' to 'master_tasks' table...")
                conn.execute(text("ALTER TABLE master_tasks ADD COLUMN verification_type VARCHAR(50) DEFAULT 'Cần chụp ảnh'"))
                conn.commit()

        # Check task_logs table for family_task_id vs task_id and parent_comment
        if inspector.has_table("task_logs"):
            columns = [col['name'] for col in inspector.get_columns("task_logs")]
            if "parent_comment" not in columns:
                logger.info("Adding 'parent_comment' to 'task_logs' table...")
                conn.execute(text("ALTER TABLE task_logs ADD COLUMN parent_comment VARCHAR(500)"))
                conn.commit()
            
            if "task_id" in columns and "family_task_id" not in columns:
                 logger.info("Renaming 'task_id' to 'family_task_id' in 'task_logs' table...")
                 conn.execute(text("ALTER TABLE task_logs RENAME COLUMN task_id TO family_task_id"))
                 conn.commit()

            if "club_task_id" not in columns:
                 logger.info("Adding 'club_task_id' to 'task_logs' table...")
                 conn.execute(text("ALTER TABLE task_logs ADD COLUMN club_task_id UUID"))
                 conn.commit()
        
        # Check family_devices
        if inspector.has_table("family_devices"):
            columns = [col['name'] for col in inspector.get_columns("family_devices")]
            if "initial_ip_address" not in columns:
                logger.info("Adding 'initial_ip_address' to 'family_devices' table...")
                conn.execute(text("ALTER TABLE family_devices ADD COLUMN initial_ip_address VARCHAR(45)"))
                conn.commit()
            if "user_agent" not in columns:
                logger.info("Adding 'user_agent' to 'family_devices' table...")
                conn.execute(text("ALTER TABLE family_devices ADD COLUMN user_agent VARCHAR(500)"))
                conn.commit()
            if "device_info" not in columns:
                logger.info("Adding 'device_info' to 'family_devices' table...")
                conn.execute(text("ALTER TABLE family_devices ADD COLUMN device_info JSON"))
                conn.commit()

        # Check audit_logs
        if inspector.has_table("audit_logs"):
            columns = [col['name'] for col in inspector.get_columns("audit_logs")]
            if "ip_address" not in columns:
                 logger.info("Adding 'ip_address' to 'audit_logs' table...")
                 conn.execute(text("ALTER TABLE audit_logs ADD COLUMN ip_address VARCHAR(45)"))
                 conn.commit()
            if "user_agent" not in columns:
                 logger.info("Adding 'user_agent' to 'audit_logs' table...")
                 conn.execute(text("ALTER TABLE audit_logs ADD COLUMN user_agent VARCHAR(500)"))
                 conn.commit()
            if "device_info" not in columns:
                 logger.info("Adding 'device_info' to 'audit_logs' table...")
                 conn.execute(text("ALTER TABLE audit_logs ADD COLUMN device_info JSON"))
                 conn.commit()

    logger.info("Custom DB migrations completed.")

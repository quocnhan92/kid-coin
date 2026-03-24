import os
from sqlalchemy import create_engine, inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db")
engine = create_engine(DATABASE_URL)

def column_exists(table_name, column_name):
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def run_migration():
    logger.info("Starting database migration check...")
    
    with engine.connect() as conn:
        # Check users table
        if not column_exists('users', 'total_earned_score'):
            logger.info("Adding 'total_earned_score' to 'users' table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN total_earned_score BIGINT DEFAULT 0"))
            conn.commit()

        # Check family_tasks table
        if not column_exists('family_tasks', 'category'):
            logger.info("Adding 'category' to 'family_tasks' table...")
            conn.execute(text("ALTER TABLE family_tasks ADD COLUMN category VARCHAR(50) DEFAULT 'Khác'"))
            conn.commit()
            
        if not column_exists('family_tasks', 'verification_type'):
            logger.info("Adding 'verification_type' to 'family_tasks' table...")
            conn.execute(text("ALTER TABLE family_tasks ADD COLUMN verification_type VARCHAR(50) DEFAULT 'Cần chụp ảnh'"))
            conn.commit()

        # Check master_tasks table
        if not column_exists('master_tasks', 'verification_type'):
            logger.info("Adding 'verification_type' to 'master_tasks' table...")
            conn.execute(text("ALTER TABLE master_tasks ADD COLUMN verification_type VARCHAR(50) DEFAULT 'Cần chụp ảnh'"))
            conn.commit()

        # Check task_logs table
        if not column_exists('task_logs', 'parent_comment'):
            logger.info("Adding 'parent_comment' to 'task_logs' table...")
            conn.execute(text("ALTER TABLE task_logs ADD COLUMN parent_comment VARCHAR(500)"))
            conn.commit()
            
        # Check family_devices table
        if not inspect(engine).has_table('family_devices'):
             logger.info("Table 'family_devices' does not exist. It will be created by app startup.")
             # The create_all in main.py will handle entirely new tables.
             
        # Convert existing task_id to family_task_id in task_logs if needed
        # This is a bit more complex. If task_id exists and family_task_id doesn't:
        if column_exists('task_logs', 'task_id') and not column_exists('task_logs', 'family_task_id'):
            logger.info("Migrating 'task_id' to 'family_task_id' in 'task_logs'...")
            conn.execute(text("ALTER TABLE task_logs RENAME COLUMN task_id TO family_task_id"))
            # Note: We skip the CHECK constraint here for simplicity in this hacky script, 
            # as it requires dropping/recreating constraints.
            conn.commit()

    logger.info("Migration check completed.")

if __name__ == "__main__":
    run_migration()

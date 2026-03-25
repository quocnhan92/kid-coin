import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable or default for local dev
# IMPORTANT: When running in Docker, the host is 'db', not 'localhost'
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db")

def get_engine_with_retry(url, retries=5, delay=2):
    logger.info(f"Test connect Database...")
    while retries > 0:
        try:
            eng = create_engine(url)
            # Chạy thử một lệnh ping/kết nối
            with eng.connect() as conn:
                pass
            logger.info("Connect Database Success")
            return eng
        except OperationalError as e:
            retries -= 1
            logger.warning(f"Connect Database Fail, Retry ... ({retries} lần còn lại)")
            time.sleep(delay)
    
    logger.error("Connect Database Error")
    raise Exception("Connect Database Error, Retried 3 round")

# Khởi tạo engine với cơ chế retry
engine = get_engine_with_retry(DATABASE_URL, retries=5, delay=2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

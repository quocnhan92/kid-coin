import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable or default for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db")

def get_engine_with_retry(url, retries=5, delay=5):
    for i in range(retries):
        try:
            # Postgres specific pool settings usually go here,
            # but we'll keep it simple for now as we're testing with SQLite.
            engine = create_engine(url)
            return engine
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay)

def get_engine(url):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return get_engine_with_retry(url, retries=5, delay=5)

# Khởi tạo engine
engine = get_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

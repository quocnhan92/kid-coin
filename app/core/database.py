from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable or default for local dev
# IMPORTANT: When running in Docker, the host is 'db', not 'localhost'
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db")

logger.info(f"Using DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

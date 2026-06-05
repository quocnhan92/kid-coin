from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
import logging
from passlib.context import CryptContext

from app.models.admin import AdminUser, AdminRole
from app.models.user_family import Family, User
from app.core.security import create_access_token
from app.services import coin_ledger_service as ledger

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_admin(db: Session, username: str, password: str) -> Optional[AdminUser]:
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


def create_admin_token(admin_id: UUID):
    return create_access_token(subject=f"admin:{admin_id}")


def list_families(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Family).offset(skip).limit(limit).all()


def adjust_user_coins(db: Session, user_id: UUID, amount: int, reason: str):
    user = db.query(User).get(user_id)
    if not user:
        return None

    ledger.adjust_admin(db, user, amount, reason)
    db.commit()
    db.refresh(user)
    return user


def seed_admin(db: Session):
    """Seed default admin if none exists."""
    if db.query(AdminUser).count() == 0:
        admin = AdminUser(
            username="admin",
            password_hash=get_password_hash("admin123"),
            display_name="System Admin",
            role=AdminRole.SUPER_ADMIN,
        )
        db.add(admin)
        db.commit()
        logger.info("Default admin created: admin/admin123")

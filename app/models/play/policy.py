"""Play kid consent & daily screen time."""
import sqlalchemy as sa
from sqlalchemy import Column, Date, DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayKidConsent(Base):
    __tablename__ = "play_kid_consents"
    __table_args__ = (sa.UniqueConstraint("kid_id", "consent_type", name="uq_play_kid_consent"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    kid_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(String(32), nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    meta_json = Column(JSONB, server_default="{}", nullable=False)


class PlayDailyScreenTime(Base):
    __tablename__ = "play_daily_screen_time"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    usage_date = Column(Date, primary_key=True)
    minutes_used = Column(Integer, server_default="0", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

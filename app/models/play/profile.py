import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayProfile(Base):
    __tablename__ = "play_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    target_grade = Column(SmallInteger, nullable=True)
    birth_year = Column(SmallInteger, nullable=True)
    active_content_pack_id = Column(String(64), nullable=False, server_default="vn_gdpt2018_candy_v1")
    preferences_json = Column(JSONB, server_default="{}", nullable=False)
    parental_soft_cap_sessions_day = Column(SmallInteger, server_default="6", nullable=False)
    parental_hard_cap_sessions_day = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

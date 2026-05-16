import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, SmallInteger, Boolean, ForeignKey, UniqueConstraint, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlaySession(Base):
    __tablename__ = "play_sessions"
    __table_args__ = (
        Index("ix_play_sessions_user_started", "user_id", "started_at"),
        Index("ix_play_sessions_game_started", "game_id", "started_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    game_id = Column(String(32), nullable=False)
    game_mode_id = Column(String(32), nullable=True)
    status = Column(String(16), server_default="active", nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    client_device_id = Column(String(64), nullable=True)
    content_pack_id = Column(String(64), nullable=True)
    manifest_hash = Column(String(64), nullable=True)
    release_id = Column(String(64), nullable=True)


class PlayEvent(Base):
    __tablename__ = "play_events"
    __table_args__ = (
        UniqueConstraint("session_id", "client_seq", name="uq_play_events_session_seq"),
        Index("ix_play_events_user_occurred", "user_id", "occurred_at"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("play_sessions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    client_seq = Column(Integer, nullable=False)
    event_type = Column(String(32), nullable=False)
    skill_unit_id = Column(String(64), nullable=True)
    level_id = Column(String(16), nullable=True)
    item_id = Column(String(128), nullable=True)
    correct = Column(Boolean, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    score_delta = Column(Integer, nullable=True)
    context_json = Column(JSONB, server_default="{}", nullable=False)


class PlaySessionSummary(Base):
    __tablename__ = "play_session_summaries"

    session_id = Column(UUID(as_uuid=True), ForeignKey("play_sessions.id"), primary_key=True)
    duration_s = Column(Numeric(8, 2), nullable=False)
    questions_count = Column(Integer, server_default="0", nullable=False)
    correct_count = Column(Integer, server_default="0", nullable=False)
    accuracy = Column(Numeric(5, 4), nullable=True)
    score = Column(BigInteger, nullable=True)
    stars_earned = Column(SmallInteger, nullable=True)
    level_id = Column(String(16), nullable=True)
    summary_json = Column(JSONB, server_default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PlayIdempotencyKey(Base):
    __tablename__ = "play_idempotency_keys"

    key = Column(String(128), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(String(64), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

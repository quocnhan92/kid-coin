import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, SmallInteger, Integer, Boolean, BigInteger, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayLevelProgress(Base):
    __tablename__ = "play_level_progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    level_id = Column(String(16), ForeignKey("play_levels.id"), primary_key=True)
    stars = Column(SmallInteger, server_default="0", nullable=False)
    best_accuracy = Column(Numeric(5, 4), nullable=True)
    best_avg_latency_ms = Column(Integer, nullable=True)
    attempts = Column(Integer, server_default="0", nullable=False)
    first_cleared_at = Column(DateTime(timezone=True), nullable=True)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    is_unlocked = Column(Boolean, server_default="false", nullable=False)


class PlaySkillMasteryAgg(Base):
    __tablename__ = "play_skill_mastery_agg"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    skill_unit_id = Column(String(64), ForeignKey("play_skill_units.id"), primary_key=True)
    rolling_accuracy = Column(Numeric(5, 4), server_default="0", nullable=False)
    rolling_avg_latency_ms = Column(Integer, server_default="0", nullable=False)
    mastery_score = Column(Numeric(5, 4), server_default="0", nullable=False)
    practice_count = Column(Integer, server_default="0", nullable=False)
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)


class PlayUserGameStats(Base):
    __tablename__ = "play_user_game_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "game_id", "game_mode_id", name="uq_play_user_game_stats"),
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    game_id = Column(String(32), ForeignKey("play_games.id"), primary_key=True)
    game_mode_id = Column(String(32), primary_key=True, server_default="")
    high_score = Column(BigInteger, server_default="0", nullable=False)
    high_score_at = Column(DateTime(timezone=True), nullable=True)
    total_sessions = Column(Integer, server_default="0", nullable=False)
    total_play_time_s = Column(Integer, server_default="0", nullable=False)
    total_questions = Column(Integer, server_default="0", nullable=False)
    total_correct = Column(Integer, server_default="0", nullable=False)
    extra_json = Column(JSONB, server_default="{}", nullable=False)


class PlayModeProgress(Base):
    __tablename__ = "play_mode_progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    game_mode_id = Column(String(32), ForeignKey("play_game_modes.id"), primary_key=True)
    tier_key = Column(String(8), primary_key=True)
    mastery_status = Column(String(16), server_default="locked", nullable=False)
    mastery_window_json = Column(JSONB, server_default="{}", nullable=False)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    mastered_at = Column(DateTime(timezone=True), nullable=True)

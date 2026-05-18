import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayDailyRecommendation(Base):
    __tablename__ = "play_daily_recommendations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    recommendation_date = Column(Date, primary_key=True)
    items_json = Column(JSONB, server_default="[]", nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PlayParentWeeklySnapshot(Base):
    __tablename__ = "play_parent_weekly_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "week_start", name="uq_play_parent_weekly"),)

    id = Column(UUID(as_uuid=True), primary_key=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    report_json = Column(JSONB, server_default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PlayMetricsDaily(Base):
    __tablename__ = "play_metrics_daily"

    metric_date = Column(Date, primary_key=True)
    game_id = Column(String(32), ForeignKey("play_games.id"), primary_key=True)
    game_mode_id = Column(String(32), primary_key=True, server_default="")
    release_id = Column(String(64), primary_key=True, server_default="")
    dau = Column(Integer, server_default="0", nullable=False)
    new_users = Column(Integer, server_default="0", nullable=False)
    sessions_count = Column(Integer, server_default="0", nullable=False)
    avg_session_duration_s = Column(sa.Numeric(10, 2), server_default="0", nullable=False)
    d1_retention = Column(sa.Numeric(5, 4), nullable=True)
    d7_retention = Column(sa.Numeric(5, 4), nullable=True)
    avg_accuracy = Column(sa.Numeric(5, 4), nullable=True)
    paywall_views = Column(Integer, nullable=True)
    trial_starts = Column(Integer, nullable=True)

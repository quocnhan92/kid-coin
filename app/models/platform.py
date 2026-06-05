from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.db_types import JsonDocument


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint("key", "scope", "scope_value", name="uq_feature_flag_scope"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    scope = Column(String(16), default="global", nullable=False)
    scope_value = Column(String(64), nullable=True)
    description = Column(String(255), nullable=True)
    metadata_json = Column(JsonDocument, server_default="{}", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DomainEventOutbox(Base):
    __tablename__ = "domain_events_outbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(64), nullable=False, index=True)
    aggregate_type = Column(String(32), nullable=True)
    aggregate_id = Column(String(64), nullable=True)
    payload_json = Column(JsonDocument, nullable=False)
    family_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    status = Column(String(16), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

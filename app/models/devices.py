from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class FamilyDevice(Base):
    __tablename__ = "family_devices"
    __table_args__ = (
        Index("idx_device_family_id", "family_id"),
        Index("idx_device_token", "device_token"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    device_token = Column(String(255), unique=True, nullable=False)
    
    # New columns for detailed tracking
    initial_ip_address = Column(String(45), nullable=True) # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True) # Raw User-Agent string
    device_info = Column(JSON, nullable=True) # Parsed info: {os: 'iOS', browser: 'Safari', model: 'iPhone 15'}
    
    is_default = Column(Boolean, default=False) # Parent's primary device
    is_active = Column(Boolean, default=True)
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    family = relationship("Family", back_populates="devices")

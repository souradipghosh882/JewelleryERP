import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    Text, Enum as SAEnum, ForeignKey, Integer, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base


class MetalRateSession(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"


class MetalRate(Base):
    """Stores gold/silver rates updated twice daily."""
    __tablename__ = "metal_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rate_date = Column(Date, nullable=False)
    session = Column(SAEnum(MetalRateSession), nullable=False)
    gold_22k = Column(Float, nullable=False)   # per gram
    gold_18k = Column(Float, nullable=False)
    gold_24k = Column(Float, nullable=False)
    gold_14k = Column(Float, nullable=True)
    gold_9k = Column(Float, nullable=True)
    silver = Column(Float, nullable=False)     # per gram
    silver_925 = Column(Float, nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        # Only one rate per date per session
        __import__('sqlalchemy').UniqueConstraint('rate_date', 'session', name='uq_metal_rate_date_session'),
    )

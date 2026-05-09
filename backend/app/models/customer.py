import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, Enum as SAEnum, ForeignKey, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base


class CustomerKYCStatus(str, enum.Enum):
    NONE = "none"
    AADHAAR = "aadhaar"
    PAN = "pan"
    BOTH = "both"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    aadhaar_number = Column(String(12), nullable=True)  # required if purchase > 50k
    pan_number = Column(String(10), nullable=True)       # required if purchase > 2L
    kyc_status = Column(SAEnum(CustomerKYCStatus), default=CustomerKYCStatus.NONE)
    birth_date = Column(Date, nullable=True)
    anniversary_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scheme_accounts = relationship("SchemeAccount", back_populates="customer")

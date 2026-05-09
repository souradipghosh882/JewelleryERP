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


class SchemeType(str, enum.Enum):
    MONEY = "money"   # Customer deposits fixed amount monthly
    GOLD = "gold"     # Customer deposits gold weight monthly


class SchemeStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    DEFAULTED = "defaulted"


class Scheme(Base):
    """Scheme template (e.g., 11-month money scheme)."""
    __tablename__ = "schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    scheme_type = Column(SAEnum(SchemeType), nullable=False)
    duration_months = Column(Integer, nullable=False)
    monthly_amount = Column(Float, nullable=True)    # for money scheme
    monthly_gold_grams = Column(Float, nullable=True)  # for gold scheme
    bonus_month = Column(Boolean, default=True)      # shop pays one month as bonus
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("SchemeAccount", back_populates="scheme")


class SchemeAccount(Base):
    """Individual customer enrollment in a scheme."""
    __tablename__ = "scheme_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(30), unique=True, nullable=False)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(SAEnum(SchemeStatus), default=SchemeStatus.ACTIVE)
    total_paid = Column(Float, default=0.0)
    months_paid = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    scheme = relationship("Scheme", back_populates="accounts")
    customer = relationship("Customer", back_populates="scheme_accounts")
    transactions = relationship("SchemeTransaction", back_populates="account")


class SchemeTransaction(Base):
    __tablename__ = "scheme_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("scheme_accounts.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    gold_grams = Column(Float, nullable=True)
    month_number = Column(Integer, nullable=False)  # 1 to N
    payment_mode = Column(String(20), nullable=False)
    receipt_number = Column(String(30), nullable=True)
    collected_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("SchemeAccount", back_populates="transactions")

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


class RokarEntryType(str, enum.Enum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class RokarEntry(Base):
    """Daily cash flow tracking (Rokar = cash register/ledger)."""
    __tablename__ = "rokar_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_date = Column(Date, nullable=False)
    entry_type = Column(SAEnum(RokarEntryType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(300), nullable=False)
    reference_id = Column(String(100), nullable=True)  # bill number or other reference
    reference_type = Column(String(50), nullable=True)  # "pakka_sale", "kacha_sale", "expense", etc.
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BankLedgerEntry(Base):
    """Bank account transaction tracking."""
    __tablename__ = "bank_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(30), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # "credit" or "debit"
    amount = Column(Float, nullable=False)
    description = Column(String(300), nullable=False)
    reference = Column(String(100), nullable=True)  # cheque no, UTR, etc.
    balance_after = Column(Float, nullable=True)
    is_reconciled = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExpenseCategory(str, enum.Enum):
    SHOP = "shop"        # Rent, electricity, etc.
    HOME = "home"        # Owner's personal (only owner can view)
    SALARY = "salary"
    MAINTENANCE = "maintenance"
    MARKETING = "marketing"
    MISC = "misc"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_date = Column(Date, nullable=False)
    category = Column(SAEnum(ExpenseCategory), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(300), nullable=False)
    payment_mode = Column(String(20), nullable=False)
    receipt_path = Column(String(500), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

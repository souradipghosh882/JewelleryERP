from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=True)
    phone = Column(String(15), nullable=False)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    gstin = Column(String(15), nullable=True)
    pan_number = Column(String(10), nullable=True)
    bank_account = Column(String(30), nullable=True)
    bank_ifsc = Column(String(11), nullable=True)
    credit_limit = Column(Float, default=0.0)
    outstanding_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ornaments = relationship("Ornament", back_populates="vendor")
    purchases = relationship("VendorPurchase", back_populates="vendor")


class VendorPurchase(Base):
    __tablename__ = "vendor_purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_number = Column(String(30), unique=True, nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    purchase_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    balance_due = Column(Float, nullable=False)
    invoice_number = Column(String(50), nullable=True)
    invoice_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="purchases")


class Karigar(Base):
    """Artisan/craftsman who makes jewellery."""
    __tablename__ = "karigars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    phone = Column(String(15), nullable=True)
    specialty = Column(String(100), nullable=True)  # e.g., "Gold Rings", "Silver"
    address = Column(Text, nullable=True)
    rate_per_gram = Column(Float, nullable=True)    # making charge rate
    outstanding_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ornaments = relationship("Ornament", back_populates="karigar")

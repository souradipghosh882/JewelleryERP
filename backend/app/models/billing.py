import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    Text, Enum as SAEnum, ForeignKey, Integer
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import PakkaBase, KachaBase


class PaymentMode(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"


class BillStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


# ─── Pakka Bill (with GST) ────────────────────────────────────────────────────

class PakkaSale(PakkaBase):
    __tablename__ = "pakka_sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_number = Column(String(30), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False)  # ref to shared customers
    salesman_id = Column(UUID(as_uuid=True), nullable=False)
    sale_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    metal_rate_id = Column(UUID(as_uuid=True), nullable=False)  # rate used at time of sale
    subtotal = Column(Float, nullable=False)
    gst_rate = Column(Float, nullable=False, default=0.03)
    gst_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_mode = Column(SAEnum(PaymentMode), nullable=False)
    amount_paid = Column(Float, nullable=False)
    balance_due = Column(Float, default=0.0)
    status = Column(SAEnum(BillStatus), default=BillStatus.ACTIVE)
    cancellation_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PakkaSaleItem", back_populates="sale")


class PakkaSaleItem(PakkaBase):
    __tablename__ = "pakka_sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("pakka_sales.id"), nullable=False)
    ornament_id = Column(UUID(as_uuid=True), nullable=False)
    tag_code = Column(String(30), nullable=False)
    ornament_name = Column(String(200), nullable=False)
    metal_type = Column(String(20), nullable=False)
    net_weight = Column(Float, nullable=False)
    gold_rate = Column(Float, nullable=False)
    gold_value = Column(Float, nullable=False)
    making_charge_type = Column(String(20), nullable=False)
    making_charge_value = Column(Float, nullable=False)
    making_charge_amount = Column(Float, nullable=False)
    stone_value = Column(Float, default=0.0)
    hallmark_charge = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    item_subtotal = Column(Float, nullable=False)

    sale = relationship("PakkaSale", back_populates="items")


# ─── Kacha Bill (no GST) ──────────────────────────────────────────────────────

class KachaSale(KachaBase):
    __tablename__ = "kacha_sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_number = Column(String(30), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=True)  # optional for kacha
    salesman_id = Column(UUID(as_uuid=True), nullable=False)
    sale_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    metal_rate_id = Column(UUID(as_uuid=True), nullable=False)
    subtotal = Column(Float, nullable=False)
    old_gold_value = Column(Float, default=0.0)      # old gold exchange deduction
    old_gold_weight = Column(Float, default=0.0)     # in grams
    old_gold_purity = Column(String(10), nullable=True)
    total_amount = Column(Float, nullable=False)     # subtotal - old_gold_value
    payment_mode = Column(SAEnum(PaymentMode), nullable=False)
    amount_paid = Column(Float, nullable=False)
    balance_due = Column(Float, default=0.0)
    status = Column(SAEnum(BillStatus), default=BillStatus.ACTIVE)
    cancellation_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("KachaSaleItem", back_populates="sale")


class KachaSaleItem(KachaBase):
    __tablename__ = "kacha_sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("kacha_sales.id"), nullable=False)
    ornament_id = Column(UUID(as_uuid=True), nullable=False)
    tag_code = Column(String(30), nullable=False)
    ornament_name = Column(String(200), nullable=False)
    metal_type = Column(String(20), nullable=False)
    net_weight = Column(Float, nullable=False)
    gold_rate = Column(Float, nullable=False)
    gold_value = Column(Float, nullable=False)
    making_charge_type = Column(String(20), nullable=False)
    making_charge_value = Column(Float, nullable=False)
    making_charge_amount = Column(Float, nullable=False)
    stone_value = Column(Float, default=0.0)
    hallmark_charge = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    item_subtotal = Column(Float, nullable=False)

    sale = relationship("KachaSale", back_populates="items")

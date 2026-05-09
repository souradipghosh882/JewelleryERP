from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.billing import PaymentMode


class SaleItemCreate(BaseModel):
    ornament_id: str
    # Override making charge if needed (owner only)
    making_charge_override: Optional[float] = None


class PakkaSaleCreate(BaseModel):
    customer_id: str
    items: List[SaleItemCreate]
    payment_mode: PaymentMode
    amount_paid: float
    notes: Optional[str] = None

    @field_validator("payment_mode")
    @classmethod
    def pakka_payment_mode(cls, v: PaymentMode) -> PaymentMode:
        # Pakka bills are mandatory for card/UPI payments
        # Cash is also allowed for pakka
        return v


class KachaSaleCreate(BaseModel):
    customer_id: Optional[str] = None
    items: List[SaleItemCreate]
    payment_mode: PaymentMode
    amount_paid: float
    old_gold_weight: float = 0.0
    old_gold_purity: Optional[str] = None
    old_gold_rate: float = 0.0
    notes: Optional[str] = None

    @field_validator("payment_mode")
    @classmethod
    def kacha_must_be_cash(cls, v: PaymentMode) -> PaymentMode:
        if v != PaymentMode.CASH:
            raise ValueError("Kacha bills only support cash payments")
        return v


class SaleItemResponse(BaseModel):
    id: str
    ornament_id: str
    tag_code: str
    ornament_name: str
    metal_type: str
    net_weight: float
    gold_rate: float
    gold_value: float
    making_charge_amount: float
    stone_value: float
    hallmark_charge: float
    other_charges: float
    item_subtotal: float

    class Config:
        from_attributes = True


class PakkaSaleResponse(BaseModel):
    id: str
    bill_number: str
    customer_id: str
    salesman_id: str
    sale_date: datetime
    items: List[SaleItemResponse]
    subtotal: float
    gst_rate: float
    gst_amount: float
    total_amount: float
    payment_mode: PaymentMode
    amount_paid: float
    balance_due: float
    status: str

    class Config:
        from_attributes = True


class KachaSaleResponse(BaseModel):
    id: str
    bill_number: str
    customer_id: Optional[str]
    salesman_id: str
    sale_date: datetime
    items: List[SaleItemResponse]
    subtotal: float
    old_gold_value: float
    old_gold_weight: float
    total_amount: float
    payment_mode: PaymentMode
    amount_paid: float
    balance_due: float
    status: str

    class Config:
        from_attributes = True


class CancelBillRequest(BaseModel):
    reason: str

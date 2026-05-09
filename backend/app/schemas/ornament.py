from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.ornament import MetalType, OrnamentCategory, OrnamentStatus


class OrnamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    metal_type: MetalType
    category: OrnamentCategory
    gross_weight: float
    net_weight: float
    stone_weight: float = 0.0
    stone_type: Optional[str] = None
    stone_rate: float = 0.0
    purity: Optional[str] = None
    making_charge_type: str = "percent"
    making_charge_value: float
    hallmark_charge: float = 0.0
    other_charges: float = 0.0
    vendor_id: Optional[str] = None
    karigar_id: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("net_weight")
    @classmethod
    def net_weight_valid(cls, v: float, info) -> float:
        if v <= 0:
            raise ValueError("Net weight must be positive")
        return v

    @field_validator("making_charge_type")
    @classmethod
    def validate_making_type(cls, v: str) -> str:
        if v not in ("percent", "per_gram"):
            raise ValueError("making_charge_type must be 'percent' or 'per_gram'")
        return v


class OrnamentCreate(OrnamentBase):
    pass


class OrnamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    gross_weight: Optional[float] = None
    net_weight: Optional[float] = None
    stone_weight: Optional[float] = None
    stone_rate: Optional[float] = None
    making_charge_type: Optional[str] = None
    making_charge_value: Optional[float] = None
    hallmark_charge: Optional[float] = None
    other_charges: Optional[float] = None
    status: Optional[OrnamentStatus] = None
    notes: Optional[str] = None


class OrnamentResponse(OrnamentBase):
    id: str
    tag_code: str
    status: OrnamentStatus
    photo_path: Optional[str] = None
    barcode_path: Optional[str] = None
    qr_path: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class OrnamentPriceEstimate(BaseModel):
    """Real-time price calculation for an ornament."""
    ornament_id: str
    tag_code: str
    name: str
    net_weight: float
    gold_rate: float
    gold_value: float
    making_charge_amount: float
    stone_value: float
    hallmark_charge: float
    other_charges: float
    subtotal: float
    gst_amount: float          # for pakka
    pakka_total: float
    kacha_total: float         # subtotal (no GST)
    old_gold_deduction: float = 0.0
    kacha_after_exchange: float = 0.0

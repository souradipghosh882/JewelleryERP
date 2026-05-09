from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.models.metal_rate import MetalRateSession


class MetalRateCreate(BaseModel):
    rate_date: date
    session: MetalRateSession
    gold_22k: float
    gold_18k: float
    gold_24k: float
    gold_14k: Optional[float] = None
    gold_9k: Optional[float] = None
    silver: float
    silver_925: Optional[float] = None


class MetalRateResponse(MetalRateCreate):
    id: str
    updated_by: str
    created_at: str

    class Config:
        from_attributes = True


class CurrentRates(BaseModel):
    """Latest rates (morning or afternoon based on time)."""
    rate_date: date
    session: MetalRateSession
    gold_22k: float
    gold_18k: float
    gold_24k: float
    gold_14k: Optional[float] = None
    gold_9k: Optional[float] = None
    silver: float
    silver_925: Optional[float] = None
    is_stale: bool = False  # True if rates not updated today

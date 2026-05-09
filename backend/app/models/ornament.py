import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    Text, Enum as SAEnum, ForeignKey, Integer
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base


class MetalType(str, enum.Enum):
    GOLD_22K = "gold_22k"
    GOLD_18K = "gold_18k"
    GOLD_24K = "gold_24k"
    GOLD_14K = "gold_14k"
    GOLD_9K = "gold_9k"
    SILVER = "silver"
    SILVER_UTENSIL = "silver_utensil"
    SILVER_925 = "silver_925"


class OrnamentCategory(str, enum.Enum):
    RING = "RNG"
    NECKLACE = "NCK"
    EARRING = "EAR"
    BANGLE = "BNG"
    BRACELET = "BRC"
    CHAIN = "CHN"
    PENDANT = "PND"
    ANKLET = "ANK"
    MANGALSUTRA = "MGS"
    NOSERING = "NSR"
    UTENSIL = "UTN"
    OTHER = "OTH"


class OrnamentStatus(str, enum.Enum):
    IN_STOCK = "in_stock"
    SOLD = "sold"
    ON_APPROVAL = "on_approval"
    RETURNED = "returned"
    MELTED = "melted"
    REPAIRED = "repaired"


class Ornament(Base):
    __tablename__ = "ornaments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tag_code = Column(String(30), unique=True, nullable=False)  # G22-RNG-000123
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    metal_type = Column(SAEnum(MetalType), nullable=False)
    category = Column(SAEnum(OrnamentCategory), nullable=False)
    gross_weight = Column(Float, nullable=False)   # in grams
    net_weight = Column(Float, nullable=False)     # after deducting stone/other weight
    stone_weight = Column(Float, default=0.0)
    stone_type = Column(String(100), nullable=True)
    stone_rate = Column(Float, default=0.0)       # per gram or per piece
    purity = Column(String(10), nullable=True)     # e.g., "22K", "925"
    making_charge_type = Column(String(20), default="percent")  # "percent" or "per_gram"
    making_charge_value = Column(Float, nullable=False)
    hallmark_charge = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    karigar_id = Column(UUID(as_uuid=True), ForeignKey("karigars.id"), nullable=True)
    status = Column(SAEnum(OrnamentStatus), default=OrnamentStatus.IN_STOCK)
    photo_path = Column(String(500), nullable=True)
    barcode_path = Column(String(500), nullable=True)
    qr_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="ornaments")
    karigar = relationship("Karigar", back_populates="ornaments")

    @staticmethod
    def generate_tag_code(metal_type: MetalType, category: OrnamentCategory, serial: int) -> str:
        metal_map = {
            MetalType.GOLD_22K: "G22",
            MetalType.GOLD_18K: "G18",
            MetalType.GOLD_24K: "G24",
            MetalType.GOLD_14K: "G14",
            MetalType.GOLD_9K: "G09",
            MetalType.SILVER: "SLV",
            MetalType.SILVER_UTENSIL: "SUP",
            MetalType.SILVER_925: "S92",
        }
        return f"{metal_map[metal_type]}-{category.value}-{serial:06d}"

from typing import Optional
from sqlalchemy.orm import Session
from app.models.ornament import Ornament, MetalType
from app.models.metal_rate import MetalRate
from app.core.config import settings


def get_rate_for_metal(metal_rate: MetalRate, metal_type: MetalType) -> float:
    rate_map = {
        MetalType.GOLD_22K: metal_rate.gold_22k,
        MetalType.GOLD_18K: metal_rate.gold_18k,
        MetalType.GOLD_24K: metal_rate.gold_24k,
        MetalType.GOLD_14K: metal_rate.gold_14k or metal_rate.gold_18k * 0.75,
        MetalType.GOLD_9K: metal_rate.gold_9k or metal_rate.gold_18k * 0.5,
        MetalType.SILVER: metal_rate.silver,
        MetalType.SILVER_UTENSIL: metal_rate.silver,
        MetalType.SILVER_925: metal_rate.silver_925 or metal_rate.silver * 0.925,
    }
    return rate_map.get(metal_type, metal_rate.gold_22k)


def calculate_making_charge(
    ornament: Ornament,
    gold_rate: float,
) -> float:
    if ornament.making_charge_type == "percent":
        return (ornament.making_charge_value / 100) * gold_rate * ornament.net_weight
    else:  # per_gram
        return ornament.making_charge_value * ornament.net_weight


def calculate_item_subtotal(ornament: Ornament, metal_rate: MetalRate) -> dict:
    gold_rate = get_rate_for_metal(metal_rate, ornament.metal_type)
    gold_value = ornament.net_weight * gold_rate
    making_charge_amount = calculate_making_charge(ornament, gold_rate)
    stone_value = ornament.stone_weight * ornament.stone_rate if ornament.stone_weight else 0.0
    subtotal = (
        gold_value
        + making_charge_amount
        + stone_value
        + ornament.hallmark_charge
        + ornament.other_charges
    )
    return {
        "gold_rate": gold_rate,
        "gold_value": round(gold_value, 2),
        "making_charge_amount": round(making_charge_amount, 2),
        "stone_value": round(stone_value, 2),
        "hallmark_charge": ornament.hallmark_charge,
        "other_charges": ornament.other_charges,
        "item_subtotal": round(subtotal, 2),
    }


def calculate_pakka_total(subtotal: float, gst_rate: float = None) -> dict:
    rate = gst_rate or settings.GST_RATE
    gst_amount = round(subtotal * rate, 2)
    total = round(subtotal + gst_amount, 2)
    return {"gst_rate": rate, "gst_amount": gst_amount, "total_amount": total}


def calculate_old_gold_value(
    weight_grams: float,
    purity: str,
    current_24k_rate: float,
) -> float:
    """Calculate value of old gold being exchanged."""
    purity_map = {
        "22K": 22 / 24,
        "18K": 18 / 24,
        "24K": 1.0,
        "14K": 14 / 24,
        "9K": 9 / 24,
    }
    purity_factor = purity_map.get(purity.upper(), 22 / 24)
    return round(weight_grams * purity_factor * current_24k_rate, 2)

import pytest
from app.models.ornament import Ornament, MetalType, OrnamentCategory


def test_generate_tag_code_gold_ring():
    code = Ornament.generate_tag_code(MetalType.GOLD_22K, OrnamentCategory.RING, 1)
    assert code == "G22-RNG-000001"


def test_generate_tag_code_silver_utensil():
    code = Ornament.generate_tag_code(MetalType.SILVER_UTENSIL, OrnamentCategory.UTENSIL, 99)
    assert code == "SUP-UTN-000099"


def test_generate_tag_code_gold_18k_necklace():
    code = Ornament.generate_tag_code(MetalType.GOLD_18K, OrnamentCategory.NECKLACE, 1000)
    assert code == "G18-NCK-001000"


def test_generate_tag_code_6_digit_serial():
    code = Ornament.generate_tag_code(MetalType.GOLD_22K, OrnamentCategory.RING, 999999)
    assert code == "G22-RNG-999999"

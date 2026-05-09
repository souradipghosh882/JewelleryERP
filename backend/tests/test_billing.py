import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.services.billing_service import (
    calculate_making_charge,
    calculate_pakka_total,
    calculate_old_gold_value,
    get_rate_for_metal,
)
from app.models.ornament import MetalType
from app.models.metal_rate import MetalRate
from datetime import date


# ─── Billing Service Unit Tests ───────────────────────────────────────────────

def _make_rate(**kwargs) -> MagicMock:
    rate = MagicMock(spec=MetalRate)
    rate.gold_22k = kwargs.get("gold_22k", 7000.0)
    rate.gold_18k = kwargs.get("gold_18k", 5800.0)
    rate.gold_24k = kwargs.get("gold_24k", 7650.0)
    rate.gold_14k = kwargs.get("gold_14k", None)
    rate.gold_9k = kwargs.get("gold_9k", None)
    rate.silver = kwargs.get("silver", 90.0)
    rate.silver_925 = kwargs.get("silver_925", None)
    return rate


def _make_ornament(**kwargs) -> MagicMock:
    o = MagicMock()
    o.metal_type = kwargs.get("metal_type", MetalType.GOLD_22K)
    o.net_weight = kwargs.get("net_weight", 10.0)
    o.stone_weight = kwargs.get("stone_weight", 0.0)
    o.stone_rate = kwargs.get("stone_rate", 0.0)
    o.making_charge_type = kwargs.get("making_charge_type", "percent")
    o.making_charge_value = kwargs.get("making_charge_value", 12.0)
    o.hallmark_charge = kwargs.get("hallmark_charge", 45.0)
    o.other_charges = kwargs.get("other_charges", 0.0)
    return o


def test_get_rate_for_gold_22k():
    rate = _make_rate(gold_22k=7000.0)
    assert get_rate_for_metal(rate, MetalType.GOLD_22K) == 7000.0


def test_get_rate_for_silver():
    rate = _make_rate(silver=90.0)
    assert get_rate_for_metal(rate, MetalType.SILVER) == 90.0


def test_making_charge_percent():
    ornament = _make_ornament(making_charge_type="percent", making_charge_value=12.0, net_weight=10.0)
    # 12% of 7000 * 10g = 8400
    charge = calculate_making_charge(ornament, gold_rate=7000.0)
    assert charge == pytest.approx(8400.0)


def test_making_charge_per_gram():
    ornament = _make_ornament(making_charge_type="per_gram", making_charge_value=500.0, net_weight=5.0)
    charge = calculate_making_charge(ornament, gold_rate=7000.0)
    assert charge == pytest.approx(2500.0)


def test_pakka_total_calculation():
    result = calculate_pakka_total(10000.0)
    assert result["gst_amount"] == pytest.approx(300.0)
    assert result["total_amount"] == pytest.approx(10300.0)
    assert result["gst_rate"] == 0.03


def test_pakka_total_custom_gst_rate():
    result = calculate_pakka_total(10000.0, gst_rate=0.05)
    assert result["gst_amount"] == pytest.approx(500.0)
    assert result["total_amount"] == pytest.approx(10500.0)


def test_old_gold_value_22k():
    # 10g of 22K at 24K rate of 7650 = 10 * (22/24) * 7650
    value = calculate_old_gold_value(10.0, "22K", 7650.0)
    expected = round(10 * (22 / 24) * 7650.0, 2)
    assert value == pytest.approx(expected)


def test_old_gold_value_24k():
    value = calculate_old_gold_value(5.0, "24K", 7650.0)
    assert value == pytest.approx(5.0 * 7650.0)


def test_silver_925_fallback():
    rate = _make_rate(silver=90.0, silver_925=None)
    r = get_rate_for_metal(rate, MetalType.SILVER_925)
    assert r == pytest.approx(90.0 * 0.925)


# ─── API Integration Tests (using TestClient) ─────────────────────────────────

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_invalid_credentials():
    response = client.post("/api/v1/auth/login", json={
        "phone": "9999999999",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    response = client.get("/api/v1/inventory/ornaments")
    assert response.status_code == 403


def test_scan_nonexistent_tag():
    # Without auth should fail
    response = client.get("/api/v1/inventory/scan/INVALID-TAG-CODE")
    assert response.status_code in (401, 403)

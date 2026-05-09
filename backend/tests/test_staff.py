import pytest
from app.models.staff import Staff
from datetime import datetime


def test_generate_staff_code():
    dt = datetime(2026, 3, 15)
    code = Staff.generate_staff_code(dt, 10)
    assert code == "STF-0326-0010"


def test_generate_staff_code_january():
    dt = datetime(2025, 1, 5)
    code = Staff.generate_staff_code(dt, 1)
    assert code == "STF-0125-0001"


def test_generate_staff_code_max_sequence():
    dt = datetime(2026, 12, 31)
    code = Staff.generate_staff_code(dt, 9999)
    assert code == "STF-1226-9999"

import pytest
from train_fare import base_fare, concession, tatkal_charge

def test_base_fare_valid():
    assert base_fare("SL", 500) == 500
    assert base_fare("1A", 10) == 50  # Tests minimum fare check (< 50)

def test_base_fare_exceptions():
    with pytest.raises(ValueError, match="unknown class"):
        base_fare("UNKNOWN", 100)
    with pytest.raises(ValueError, match="invalid distance"):
        base_fare("SL", 0)

def test_concession_tatkal_and_ages():
    assert concession(30, "M", True) == 0       # Tatkal is True
    assert concession(3, "M", False) == 100     # Age < 5
    assert concession(10, "M", False) == 50     # Age <= 12
    assert concession(65, "F", False) == 50     # Senior Female
    assert concession(65, "M", False) == 40     # Senior Male
    assert concession(30, "M", False) == 0      # Regular adult

def test_tatkal_charge_classes_and_limits():
    assert tatkal_charge("SL", 500) == 100      # SL class, charge < 100 -> clamped to 100
    assert tatkal_charge("3A", 2000) == 400     # Non-SL class, charge > 400 -> clamped to 400
    assert tatkal_charge("3A", 500) == 150      # Non-SL class, normal range (500 * 3 // 10 = 150)
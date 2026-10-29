import pytest
from train_fare import base_fare, concession, tatkal_charge

# --- Base Fare Branch Tests ---
def test_base_fare_unknown_class():
    with pytest.raises(ValueError):
        base_fare("INVALID", 100)

def test_base_fare_invalid_distance():
    with pytest.raises(ValueError):
        base_fare("SL", -10)

def test_base_fare_normal():
    assert base_fare("SL", 100) == 100

def test_base_fare_min_fare_clamp():
    # RATE_PER_KM["SL"] * 10 = 10, which is < 50, so it clamps to 50
    assert base_fare("SL", 10) == 50


# --- Concession Branch Tests ---
def test_concession_is_tatkal_true():
    assert concession(25, "M", True) == 0

def test_concession_age_under_5():
    assert concession(2, "M", False) == 100

def test_concession_age_between_5_and_12():
    assert concession(10, "M", False) == 50

def test_concession_senior_female():
    assert concession(65, "F", False) == 50

def test_concession_senior_male():
    assert concession(65, "M", False) == 40

def test_concession_regular_adult():
    assert concession(30, "M", False) == 0


# --- Tatkal Charge Branch Tests ---
def test_tatkal_charge_sleeper_low_limit():
    # SL: 500 // 10 = 50, which is < 100 -> clamped to 100
    assert tatkal_charge("SL", 500) == 100

def test_tatkal_charge_sleeper_high_limit():
    # SL: 5000 // 10 = 500, which is > 400 -> clamped to 400
    assert tatkal_charge("SL", 5000) == 400

def test_tatkal_charge_non_sleeper_normal():
    # 3A: 300 * 3 // 10 = 90, which is < 100 -> clamped to 100
    assert tatkal_charge("3A", 300) == 100

def test_tatkal_charge_non_sleeper_high_limit():
    # 3A: 2000 * 3 // 10 = 600, which is > 400 -> clamped to 400
    assert tatkal_charge("3A", 2000) == 400
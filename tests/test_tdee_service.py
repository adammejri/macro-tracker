import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tdee_service import calculate_bmr, calculate_targets, get_net_burn

def test_bmr_male():
    bmr = calculate_bmr(78, 183, 27, "male")
    assert bmr == pytest.approx(1794.75, rel=1e-2)

def test_bmr_female():
    bmr = calculate_bmr(60, 165, 25, "female")
    assert bmr == pytest.approx(1345.25, rel=1e-2)

def test_bmr_case_insensitive():
    bmr_lower = calculate_bmr(78, 183, 27, "male")
    bmr_upper = calculate_bmr(78, 183, 27, "Male")
    assert bmr_lower == bmr_upper

def test_net_burn_no_negative():
    result = get_net_burn(1800, 10, 600)
    assert result >= 0

def test_net_burn_positive():
    result = get_net_burn(1800, 500, 60)
    assert result > 0

def test_calculate_targets_protein():
    targets = calculate_targets(78, 2200)
    assert targets["protein_target"] == pytest.approx(179.4, rel=1e-2)

def test_calculate_targets_calories():
    targets = calculate_targets(78, 2200)
    assert targets["calorie_target"] == 2200

def test_calculate_targets_no_negative_macros():
    targets = calculate_targets(78, 2200)
    assert targets["fat_target"]   >= 0
    assert targets["carbs_target"] >= 0
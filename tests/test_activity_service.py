import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tdee_service import calculate_tdee

class MockActivityType:
    def __init__(self, metric, met=None, kcal_km=None):
        self._data = {
            "metric": metric,
            "met_value": met,
            "kcal_per_kg_per_km": kcal_km
        }
    def __getitem__(self, key):
        return self._data[key]

def test_tdee_no_activities():
    result = calculate_tdee(78, 183, 27, "male", 5000, [])
    assert result["tdee"] > 0
    assert result["exercise_net"] == 0
    assert result["step_burn"] > 0

def test_tdee_higher_with_more_steps():
    result_low  = calculate_tdee(78, 183, 27, "male", 2000, [])
    result_high = calculate_tdee(78, 183, 27, "male", 10000, [])
    assert result_high["tdee"] > result_low["tdee"]

def test_tdee_skips_unknown_activity():
    result = calculate_tdee(78, 183, 27, "male", 5000, [
        {"type": "nonexistent_activity", "duration": 60}
    ])
    assert "nonexistent_activity" in result["skipped"]

def test_tdee_bmr_always_positive():
    result = calculate_tdee(78, 183, 27, "male", 0, [])
    assert result["bmr"] > 0

def test_tdee_tef_is_fraction_of_total():
    result = calculate_tdee(78, 183, 27, "male", 5000, [])
    assert result["tef"] == round(result["tdee"] * 0.091)
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.meal_service import search_and_prepare_food

class MockFoodRow:
    def __init__(self):
        self._data = {
            "name": "Kycklingfilé",
            "brand": "GARANT",
            "calories": 100.0,
            "protein": 21.0,
            "carbs": 0.5,
            "fat": 2.0
        }
    def __getitem__(self, key):
        return self._data[key]

def test_prepare_food_correct_scaling():
    food_row = MockFoodRow()
    result = search_and_prepare_food(food_row, 200)

    assert result["calories"] == 200.0
    assert result["protein"]  == 42.0
    assert result["carbs"]    == 1.0
    assert result["fat"]      == 4.0
    assert result["grams"]    == 200

def test_prepare_food_half_portion():
    food_row = MockFoodRow()
    result = search_and_prepare_food(food_row, 50)

    assert result["calories"] == 50.0
    assert result["protein"]  == 10.5
    assert result["carbs"]    == 0.2
    assert result["fat"]      == 1.0

def test_prepare_food_preserves_name_and_brand():
    food_row = MockFoodRow()
    result = search_and_prepare_food(food_row, 100)

    assert result["name"]  == "Kycklingfilé"
    assert result["brand"] == "GARANT"
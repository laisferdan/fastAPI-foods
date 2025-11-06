import pytest
from datetime import datetime

from fast_zero.schemas.consumptions import ConsumptionIn, MealType


def test_consumption_in_accepts_enum_values():
    payload = {
        "recipe_id": 1,
        "kcal": 100,
        "tipo_refeicao": MealType.almoco,
        "consumed_at": datetime(2025, 1, 1),
    }
    obj = ConsumptionIn(**payload)
    assert obj.tipo_refeicao == MealType.almoco


def test_consumption_in_rejects_invalid_meal_type():
    payload = {
        "recipe_id": 1,
        "kcal": 100,
        "tipo_refeicao": "invalid",
        "consumed_at": datetime(2025, 1, 1),
    }
    with pytest.raises(ValueError):
        ConsumptionIn(**payload)

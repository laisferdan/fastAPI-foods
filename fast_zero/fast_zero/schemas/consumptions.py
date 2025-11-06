from datetime import datetime

from pydantic import BaseModel, PositiveInt


class ConsumptionIn(BaseModel):
    recipe_id: PositiveInt
    kcal: PositiveInt
    tipo_refeicao: str
    consumed_at: datetime | None = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "recipe_id": 1,
                "kcal": 600,
                "tipo_refeicao": "almoço",
                "consumed_at": "2025-01-01T12:00:00",
            }
        }
    }


class ConsumptionOut(ConsumptionIn):
    id: int
    user_id: int

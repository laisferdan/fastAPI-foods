from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class UserProfileIn(BaseModel):
    sexo: str = Field(pattern=r"^(M|F|O)$")
    idade: PositiveInt
    peso_kg: PositiveFloat
    altura_cm: PositiveFloat
    nivel_atividade: float = Field(..., description="1.2, 1.375, 1.55, 1.725, 1.9")
    model_config = {
        "json_schema_extra": {
            "example": {
                "sexo": "M",
                "idade": 30,
                "peso_kg": 70.0,
                "altura_cm": 175.0,
                "nivel_atividade": 1.55,
            }
        }
    }


class UserProfileOut(UserProfileIn):
    user_id: int

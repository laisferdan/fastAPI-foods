from pydantic import BaseModel, PositiveFloat, PositiveInt


class RecommendationItem(BaseModel):
    recipe_id: PositiveInt
    nome_refeicao: str
    kcal: PositiveFloat
    tipo: str
    adequacao_percentual: float


class RecommendationList(BaseModel):
    items: list[RecommendationItem]

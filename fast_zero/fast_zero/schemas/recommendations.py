from pydantic import BaseModel, PositiveInt


class RecommendationItem(BaseModel):
    recipe_id: PositiveInt
    nome_refeicao: str
    kcal: PositiveInt
    tipo: str
    adequacao_percentual: float


class RecommendationList(BaseModel):
    items: list[RecommendationItem]

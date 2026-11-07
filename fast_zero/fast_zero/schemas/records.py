from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, PositiveInt


class RecordMealType(str, Enum):
    cafe_da_manha = 'cafe_da_manha'
    almoco = 'almoço'
    jantar = 'jantar'


class RecordCreate(BaseModel):
    data: date
    tipo_refeicao: RecordMealType
    recipe_id: PositiveInt
    quantidade_g: float = Field(gt=0)


class RecordPublic(BaseModel):
    id: int
    data: date
    tipo_refeicao: str
    recipe_id: int
    quantidade_g: float | None
    kcal: int
    nome_alimento: str
    nome_categoria: str


class RecordList(BaseModel):
    records: list[RecordPublic]

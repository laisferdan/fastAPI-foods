from pydantic import BaseModel, ConfigDict, Field

QUANTIDADE_PATTERN = r'^\d+(\.\d+)?g$'


class RecipeCreate(BaseModel):
    nome_refeicao: str
    nome_alimento: str = Field(min_length=1)
    nome_categoria: str
    quantidade: str = Field(pattern=QUANTIDADE_PATTERN, examples=['250g'])
    kcal: float = Field(ge=0)
    dia_semana: str


class RecipePublic(RecipeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RecipeList(BaseModel):
    recipes: list[RecipePublic]

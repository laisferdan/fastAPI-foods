from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    # Exercício
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class RecipeModel:
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome_refeicao: Mapped[str]
    nome_alimento: Mapped[str]
    nome_categoria: Mapped[str]
    quantidade: Mapped[str]
    kcal: Mapped[int]
    dia_semana: Mapped[str]


@table_registry.mapped_as_dataclass
class UserProfile:
    __tablename__ = 'user_profiles'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int]
    sexo: Mapped[str]
    idade: Mapped[int]
    peso_kg: Mapped[float]
    altura_cm: Mapped[float]
    nivel_atividade: Mapped[float]
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class ConsumptionLog:
    __tablename__ = 'consumption_logs'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int]
    recipe_id: Mapped[int]
    kcal: Mapped[int]
    tipo_refeicao: Mapped[str]
    consumed_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class RecommendationFeedback:
    __tablename__ = 'recommendation_feedback'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int]
    recipe_id: Mapped[int]
    feedback: Mapped[str]  # like | dislike
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

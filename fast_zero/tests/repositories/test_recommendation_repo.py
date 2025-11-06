from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.fast_zero.models.models import (
    ConsumptionLog,
    RecipeModel,
    RecommendationFeedback,
    User,
    table_registry,
)
from fast_zero.fast_zero.repositories.recommendation import (
    kcal_consumed_on,
    recent_categories,
    user_feedback_map,
)


def setup_db():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)
    return engine


def test_kcal_consumed_on():
    engine = setup_db()
    with Session(engine) as s:
        u = User(username='u', password='p', email='e@e.com')
        s.add(u)
        s.flush()
        r = RecipeModel(
            nome_refeicao='almoço',
            nome_alimento='arroz',
            nome_categoria='grãos',
            quantidade='100g',
            kcal=200,
            dia_semana='segunda',
        )
        s.add(r)
        s.flush()
        s.add(
            ConsumptionLog(
                user_id=u.id,
                recipe_id=r.id,
                kcal=200,
                tipo_refeicao='almoço',
                consumed_at=datetime(2024, 1, 1, 12, 0, 0),
            )
        )
        s.commit()
        total = kcal_consumed_on(s, u.id, datetime(2024, 1, 1).date())
        assert total == 200


def test_recent_categories_and_feedback():
    engine = setup_db()
    with Session(engine) as s:
        u = User(username='u2', password='p', email='e2@e.com')
        s.add(u)
        s.flush()
        r1 = RecipeModel(
            nome_refeicao='jantar',
            nome_alimento='frango',
            nome_categoria='proteína',
            quantidade='150g',
            kcal=300,
            dia_semana='terça',
        )
        r2 = RecipeModel(
            nome_refeicao='lanche',
            nome_alimento='maçã',
            nome_categoria='fruta',
            quantidade='1 unidade',
            kcal=80,
            dia_semana='terça',
        )
        s.add_all([r1, r2])
        s.flush()
        s.add_all(
            [
                ConsumptionLog(
                    user_id=u.id,
                    recipe_id=r1.id,
                    kcal=300,
                    tipo_refeicao='jantar',
                    consumed_at=datetime(2024, 1, 2, 20, 0, 0),
                ),
                ConsumptionLog(
                    user_id=u.id,
                    recipe_id=r2.id,
                    kcal=80,
                    tipo_refeicao='lanche',
                    consumed_at=datetime(2024, 1, 2, 10, 0, 0),
                ),
                RecommendationFeedback(
                    user_id=u.id, recipe_id=r1.id, feedback='dislike'
                ),
            ]
        )
        s.commit()

        cats = recent_categories(s, u.id)
        assert cats[0] in {'proteína', 'fruta'}

        fb = user_feedback_map(s, u.id)
        assert fb[r1.id] == 'dislike'

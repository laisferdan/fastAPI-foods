from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from fast_zero.models.models import ConsumptionLog
from fast_zero.repositories.analytics import (
    get_calories_by_day,
    get_distribution_by_meal,
    get_summary,
)


def _dt(days_offset: int) -> datetime:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=days_offset)


def _seed(session: Session, user_id: int):
    session.add_all(
        [
            ConsumptionLog(user_id=user_id, recipe_id=1, kcal=500, tipo_refeicao="almoço", consumed_at=_dt(0)),
            ConsumptionLog(user_id=user_id, recipe_id=2, kcal=300, tipo_refeicao="cafe_da_manha", consumed_at=_dt(0)),
        ]
    )
    session.add_all(
        [
            ConsumptionLog(user_id=user_id, recipe_id=3, kcal=700, tipo_refeicao="jantar", consumed_at=_dt(-1)),
            ConsumptionLog(user_id=user_id, recipe_id=4, kcal=200, tipo_refeicao="lanche", consumed_at=_dt(-1)),
        ]
    )
    session.add(
        ConsumptionLog(user_id=999, recipe_id=10, kcal=999, tipo_refeicao="almoço", consumed_at=_dt(0))
    )
    session.commit()


def test_get_summary(session: Session):
    user_id = 1
    _seed(session, user_id)

    start = _dt(-3)
    end = _dt(1)

    total_kcal, total_meals, total_foods = get_summary(session, user_id, start, end)
    assert total_kcal == 1700  
    assert total_meals == 4
    assert total_foods == 4  


def test_get_calories_by_day(session: Session):
    user_id = 1
    _seed(session, user_id)

    start = _dt(-3)
    end = _dt(1)

    points = get_calories_by_day(session, user_id, start, end)
    assert len(points) == 2
    first_day, first_kcal = points[0]
    second_day, second_kcal = points[1]
    assert first_kcal in (900, 800) or second_kcal in (900, 800)
    kcal_by_day = {p[0].date(): p[1] for p in points}
    assert kcal_by_day[_dt(-1).date()] == 900
    assert kcal_by_day[_dt(0).date()] == 800


def test_get_distribution_by_meal(session: Session):
    user_id = 1
    _seed(session, user_id)

    start = _dt(-3)
    end = _dt(1)

    items = get_distribution_by_meal(session, user_id, start, end)
    kinds = {kind for kind, _kcal, _pct in items}
    assert kinds == {"almoço", "cafe_da_manha", "jantar", "lanche"}

    lookup = {kind: (kcal, pct) for kind, kcal, pct in items}
    assert lookup["almoço"][0] == 500
    assert lookup["cafe_da_manha"][0] == 300
    assert lookup["jantar"][0] == 700
    assert lookup["lanche"][0] == 200

    assert lookup["almoço"][1] == round(500 / 1700 * 100, 2)
    assert lookup["cafe_da_manha"][1] == round(300 / 1700 * 100, 2)
    assert lookup["jantar"][1] == round(700 / 1700 * 100, 2)
    assert lookup["lanche"][1] == round(200 / 1700 * 100, 2)


def test_distribution_zero_total_returns_zero_percent(session: Session):
    user_id = 2
    session.add(ConsumptionLog(user_id=user_id, recipe_id=1, kcal=100, tipo_refeicao="almoço", consumed_at=_dt(-10)))
    session.commit()

    start = _dt(-3)
    end = _dt(1)

    items = get_distribution_by_meal(session, user_id, start, end)
    for _kind, _kcal, pct in items:
        assert pct == 0.0

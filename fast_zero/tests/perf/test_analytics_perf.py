import time
from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from fast_zero.repositories.analytics import (
    get_calories_by_day,
    get_distribution_by_meal,
    get_summary,
)
from fast_zero.tests.factories import bulk_make_consumptions, dt_midnight_utc


@pytest.mark.slow
def test_analytics_queries_should_be_fast_with_many_rows(session: Session):
    user_id = 42
    start_day = dt_midnight_utc(-30)
    items = []
    recipe = 1
    tipos = ["almoço", "jantar", "lanche", "cafe_da_manha"]
    for d in range(30):
        day = start_day + timedelta(days=d)
        for i in range(333):
            tipo = tipos[i % len(tipos)]
            kcal = (i % 700) + 100
            items.append((user_id, recipe, kcal, tipo, day))
            recipe += 1
    bulk_make_consumptions(session, items)

    start = start_day
    end = dt_midnight_utc(1)

    t0 = time.perf_counter()
    total_kcal, total_meals, total_foods = get_summary(session, user_id, start, end)
    points = get_calories_by_day(session, user_id, start, end)
    dist = get_distribution_by_meal(session, user_id, start, end)
    elapsed = time.perf_counter() - t0

    assert total_meals == len(items)
    assert len(points) >= 25 
    assert len(dist) == len(tipos)
    assert elapsed < 0.6

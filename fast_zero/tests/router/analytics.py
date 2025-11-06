from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session

from fast_zero.models.models import ConsumptionLog
from fast_zero.routes import analytics as analytics_router
from fast_zero.security import auth as auth_module
from fast_zero.database import database as db_module


def _dt(days_offset: int) -> datetime:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=days_offset)


def _seed(session: Session, user_id: int):
    session.add_all(
        [
            ConsumptionLog(user_id=user_id, recipe_id=1, kcal=500, tipo_refeicao="almoço", consumed_at=_dt(0)),
            ConsumptionLog(user_id=user_id, recipe_id=2, kcal=300, tipo_refeicao="cafe_da_manha", consumed_at=_dt(0)),
            ConsumptionLog(user_id=user_id, recipe_id=3, kcal=700, tipo_refeicao="jantar", consumed_at=_dt(-1)),
            ConsumptionLog(user_id=user_id, recipe_id=4, kcal=200, tipo_refeicao="lanche", consumed_at=_dt(-1)),
        ]
    )
    session.commit()


def _build_client_with_overrides(session: Session, user_id: int) -> TestClient:
    app = FastAPI()
    app.include_router(analytics_router.router)

    app.dependency_overrides[auth_module.get_current_user_id] = lambda: user_id

    def _override_get_session():
        yield session

    app.dependency_overrides[db_module.get_session] = _override_get_session

    return TestClient(app)


def test_summary_endpoint(session: Session):
    user_id = 1
    _seed(session, user_id)

    client = _build_client_with_overrides(session, user_id)

    resp = client.get("/analytics/me/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_kcal"] == 1700
    assert data["total_meals"] == 4
    assert data["total_foods"] == 4


def test_calories_by_day_endpoint(session: Session):
    user_id = 2
    _seed(session, user_id)

    client = _build_client_with_overrides(session, user_id)

    resp = client.get("/analytics/me/calories-by-day")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_days"] == 2
    kcal_by_day = {p["date"][:10]: p["kcal"] for p in data["points"]}
    assert list(sorted(kcal_by_day.values())) == [800, 900]


def test_distribution_by_meal_endpoint(session: Session):
    user_id = 3
    _seed(session, user_id)

    client = _build_client_with_overrides(session, user_id)

    resp = client.get("/analytics/me/distribution-by-meal")
    assert resp.status_code == 200
    data = resp.json()
    items = {i["tipo_refeicao"]: (i["kcal"], i["percent"]) for i in data["items"]}
    assert set(items.keys()) == {"almoço", "cafe_da_manha", "jantar", "lanche"}
    assert items["almoço"][0] == 500
    assert items["cafe_da_manha"][0] == 300
    assert items["jantar"][0] == 700
    assert items["lanche"][0] == 200

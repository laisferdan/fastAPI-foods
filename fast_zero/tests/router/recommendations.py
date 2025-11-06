from http import HTTPStatus
from datetime import datetime, date

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session as real_get_session
from fast_zero.models.models import (
    RecipeModel,
    User,
    UserProfile,
    table_registry,
)
from fast_zero.routes import recommendations
from fast_zero.security.auth import create_access_token


def make_app_and_db():
    engine = create_engine("sqlite:///:memory:")
    table_registry.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(recommendations.router)

    def override_get_session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[real_get_session] = override_get_session
    return app, engine


def test_recommend_without_profile_returns_message():
    app, engine = make_app_and_db()
    with Session(engine) as s:
        s.add(User(username="u", password="p", email="e@e.com"))
        s.commit()
        user_id = s.query(User).first().id

    client = TestClient(app)
    token = create_access_token(user_id)
    resp = client.get("/recomendacoes/recommend", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == HTTPStatus.OK
    assert "message" in resp.json()


def test_recommend_requires_auth():
    app, _ = make_app_and_db()
    client = TestClient(app)
    resp = client.get("/recomendacoes/recommend")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_profile_put_and_get_then_recommend_consumption_and_feedback():
    app, engine = make_app_and_db()
    with Session(engine) as s:
        u = User(username="u2", password="p", email="e2@e.com")
        s.add(u)
        s.flush()
        s.add_all(
            [
                RecipeModel(
                    nome_refeicao="almoço",
                    nome_alimento="prato 1",
                    nome_categoria="categoria A",
                    quantidade="1 porção",
                    kcal=600,
                    dia_semana="segunda",
                ),
                RecipeModel(
                    nome_refeicao="lanche",
                    nome_alimento="prato 2",
                    nome_categoria="categoria B",
                    quantidade="1 porção",
                    kcal=300,
                    dia_semana="segunda",
                ),
            ]
        )
        s.commit()
        user_id = u.id

    client = TestClient(app)

    payload = {
        "sexo": "M",
        "idade": 30,
        "peso_kg": 70.0,
        "altura_cm": 175.0,
        "nivel_atividade": 1.55,
    }
    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.put("/recomendacoes/profile", json=payload, headers=headers)
    assert r.status_code == HTTPStatus.OK

    r2 = client.get("/recomendacoes/profile", headers=headers)
    assert r2.status_code == HTTPStatus.OK
    assert r2.json()["user_id"] == user_id

    rc = client.post(
        "/recomendacoes/consumptions",
        headers=headers,
        json={
            "recipe_id": 1,
            "kcal": 600,
            "tipo_refeicao": "almoço",
            "consumed_at": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
        },
    )
    assert rc.status_code == HTTPStatus.CREATED

    rf = client.post(
        "/recomendacoes/feedback",
        headers=headers,
        json={"recipe_id": 2, "feedback": "like"},
    )
    assert rf.status_code == HTTPStatus.CREATED

    r3 = client.get("/recomendacoes/recommend", headers=headers)
    assert r3.status_code == HTTPStatus.OK
    data = r3.json()
    assert "items" in data or "message" in data
    if "items" in data:
        assert isinstance(data["items"], list)

import os
from contextlib import contextmanager
from datetime import datetime

# Antes de importar a app: banco e segredo isolados para os testes.
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['JWT_SECRET_KEY'] = 'chave-de-teste-com-mais-de-32-bytes-0123456789'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from fast_zero.app import app  # noqa: E402
from fast_zero.database.database import get_session  # noqa: E402
from fast_zero.models.models import (  # noqa: E402
    RecipeModel,
    User,
    table_registry,
)
from fast_zero.security.auth import create_access_token  # noqa: E402
from fast_zero.security.passwords import get_password_hash  # noqa: E402


@pytest.fixture
def engine():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    yield engine
    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_user(session, username, email, password):
    user = User(
        username=username,
        email=email,
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def user(session):
    return _make_user(session, 'alice', 'alice@example.com', 'secret-pass-1')


@pytest.fixture
def other_user(session):
    return _make_user(session, 'bob', 'bob@example.com', 'secret-pass-2')


def _headers(user):
    return {'Authorization': f'Bearer {create_access_token(user.id)}'}


@pytest.fixture
def auth_headers(user):
    return _headers(user)


@pytest.fixture
def other_auth_headers(other_user):
    return _headers(other_user)


@pytest.fixture
def recipe(session):
    recipe = RecipeModel(
        nome_refeicao='Almoço',
        nome_alimento='Abobrinha Recheada',
        nome_categoria='Pratos Únicos',
        quantidade='250g',
        kcal=300,
        dia_semana='Domingo',
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time

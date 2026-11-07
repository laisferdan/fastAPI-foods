from http import HTTPStatus

from sqlalchemy import select

from fast_zero.models.models import ConsumptionLog, User

NEW_USER = {
    'username': 'carol',
    'email': 'Carol@Example.com',
    'password': 'long-enough-pw',
}


def test_create_user(client, session):
    response = client.post('/users', json=NEW_USER)

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body == {
        'id': 1,
        'username': 'carol',
        'email': 'carol@example.com',
    }
    assert 'password' not in body

    stored = session.scalar(select(User))
    assert stored.password != NEW_USER['password']
    assert stored.password.startswith('$argon2')


def test_create_user_username_exists(client, user):
    response = client.post(
        '/users', json={**NEW_USER, 'username': user.username}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_exists_is_case_insensitive(client, user):
    response = client.post(
        '/users', json={**NEW_USER, 'email': user.email.upper()}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_create_user_rejects_short_password(client):
    response = client.post('/users', json={**NEW_USER, 'password': '123'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user_rejects_invalid_email(client):
    response = client.post('/users', json={**NEW_USER, 'email': 'nope'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_read_me(client, user, auth_headers):
    response = client.get('/users/me', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_me_requires_token(client):
    response = client.get('/users/me')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_old_list_and_id_routes_are_gone(client, user, auth_headers):
    listing = client.get('/users', headers=auth_headers)
    by_id = client.put(f'/users/{user.id}', json={}, headers=auth_headers)

    assert listing.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert by_id.status_code == HTTPStatus.NOT_FOUND


def test_update_me_partial(client, user, auth_headers):
    response = client.put(
        '/users/me', json={'username': 'alice2'}, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'alice2'
    assert response.json()['email'] == 'alice@example.com'


def test_update_me_password_allows_new_login(client, user, auth_headers):
    response = client.put(
        '/users/me', json={'password': 'brand-new-pass'}, headers=auth_headers
    )
    assert response.status_code == HTTPStatus.OK

    old = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    new = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'brand-new-pass'},
    )
    assert old.status_code == HTTPStatus.UNAUTHORIZED
    assert new.status_code == HTTPStatus.OK


def test_update_me_keeping_own_values_is_not_a_conflict(
    client, user, auth_headers
):
    response = client.put(
        '/users/me',
        json={'username': user.username, 'email': user.email},
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK


def test_update_me_conflicts_with_other_user(client, other_user, auth_headers):
    by_name = client.put(
        '/users/me',
        json={'username': other_user.username},
        headers=auth_headers,
    )
    by_email = client.put(
        '/users/me', json={'email': other_user.email}, headers=auth_headers
    )

    assert by_name.status_code == HTTPStatus.CONFLICT
    assert by_name.json() == {'detail': 'Username already exists'}
    assert by_email.status_code == HTTPStatus.CONFLICT
    assert by_email.json() == {'detail': 'Email already exists'}


def test_update_me_requires_token(client):
    response = client.put('/users/me', json={'username': 'zzz'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_me_removes_user_and_own_records_only(
    client, session, user, other_user, recipe, auth_headers
):
    for owner in (user, other_user):
        session.add(
            ConsumptionLog(
                user_id=owner.id,
                recipe_id=recipe.id,
                kcal=300,
                tipo_refeicao='almoço',
            )
        )
    session.commit()

    response = client.delete('/users/me', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
    assert session.get(User, user.id) is None
    remaining = session.scalars(select(ConsumptionLog)).all()
    assert [log.user_id for log in remaining] == [other_user.id]

    again = client.get('/users/me', headers=auth_headers)
    assert again.status_code == HTTPStatus.UNAUTHORIZED


def test_create_user_race_returns_conflict_not_500(client, user, monkeypatch):
    # Simula dois cadastros simultâneos: a checagem prévia não vê o outro
    # pedido, mas a constraint única do banco barra o segundo.
    monkeypatch.setattr(
        'fast_zero.routes.users._ensure_unique',
        lambda *args, **kwargs: None,
    )

    response = client.post(
        '/users', json={**NEW_USER, 'username': user.username}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists'}


def test_update_me_race_returns_conflict_not_500(
    client, other_user, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        'fast_zero.routes.users._ensure_unique',
        lambda *args, **kwargs: None,
    )

    response = client.put(
        '/users/me',
        json={'username': other_user.username},
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.CONFLICT

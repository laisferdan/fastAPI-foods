from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt

from fast_zero.security.auth import create_access_token
from fast_zero.settings.settings import Settings


def _login(client, username, password):
    return client.post(
        '/auth/token', data={'username': username, 'password': password}
    )


def test_signup_then_login_flow(client):
    created = client.post(
        '/users',
        json={
            'username': 'dana',
            'email': 'dana@example.com',
            'password': 'a-good-password',
        },
    )
    assert created.status_code == HTTPStatus.CREATED

    response = _login(client, 'dana@example.com', 'a-good-password')

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['token_type'] == 'bearer'
    me = client.get(
        '/users/me',
        headers={'Authorization': f'Bearer {body["access_token"]}'},
    )
    assert me.json()['email'] == 'dana@example.com'


def test_login_is_case_insensitive_on_email(client, user):
    response = _login(client, user.email.upper(), user.clean_password)

    assert response.status_code == HTTPStatus.OK


def test_login_token_has_expiration_and_user_id(client, user):
    token = _login(client, user.email, user.clean_password).json()[
        'access_token'
    ]

    settings = Settings()
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload['sub'] == str(user.id)
    expires = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    delta = expires - datetime.now(timezone.utc)
    assert timedelta(minutes=28) < delta <= timedelta(minutes=30)


def test_login_wrong_password(client, user):
    response = _login(client, user.email, 'not-the-password')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
    assert response.headers['www-authenticate'] == 'Bearer'


def test_login_unknown_email_has_same_error(client):
    response = _login(client, 'ghost@example.com', 'whatever-pass')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_requires_fields(client):
    response = client.post('/auth/token', data={'username': 'x@y.com'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_protected_route_without_token(client):
    response = client.get('/users/me')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers['www-authenticate'] == 'Bearer'


def test_protected_route_with_garbage_token(client):
    response = client.get(
        '/users/me', headers={'Authorization': 'Bearer not.a.jwt'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_protected_route_with_expired_token(client, user):
    token = create_access_token(user.id, expires_minutes=-1)

    response = client.get(
        '/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_signed_with_other_key_is_rejected(client, user):
    token = jwt.encode(
        {
            'sub': str(user.id),
            'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        'another-secret-key-with-more-than-32-bytes!!',
        algorithm='HS256',
    )

    response = client.get(
        '/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_without_exp_is_rejected(client, user):
    settings = Settings()
    token = jwt.encode(
        {'sub': str(user.id)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.get(
        '/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_of_deleted_user_is_rejected(client):
    token = create_access_token(12345)

    response = client.get(
        '/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

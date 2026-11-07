from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_cors_allows_only_the_frontend_origin(client):
    allowed = client.options(
        '/recipes',
        headers={
            'Origin': 'http://localhost:4200',
            'Access-Control-Request-Method': 'GET',
        },
    )
    denied = client.options(
        '/recipes',
        headers={
            'Origin': 'http://evil.example.com',
            'Access-Control-Request-Method': 'GET',
        },
    )

    assert (
        allowed.headers['access-control-allow-origin']
        == 'http://localhost:4200'
    )
    assert 'access-control-allow-origin' not in denied.headers


def test_old_accented_and_duplicated_routes_do_not_exist(client):
    for path in ('/usuários/users/', '/receitas/recipes/'):
        assert client.get(path).status_code == HTTPStatus.NOT_FOUND

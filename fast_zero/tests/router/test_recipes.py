from http import HTTPStatus

from fast_zero.models.models import ConsumptionLog

PAYLOAD = {
    'nome_refeicao': 'Jantar',
    'nome_alimento': 'Sopa de Legumes',
    'nome_categoria': 'Sopas',
    'quantidade': '300g',
    'kcal': 120.5,
    'dia_semana': 'Segunda-feira',
}


def test_recipes_require_token(client, recipe):
    assert client.get('/recipes').status_code == HTTPStatus.UNAUTHORIZED
    assert (
        client.get(f'/recipes/{recipe.id}').status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert (
        client.post('/recipes', json=PAYLOAD).status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert (
        client.put(f'/recipes/{recipe.id}', json=PAYLOAD).status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert (
        client.delete(f'/recipes/{recipe.id}').status_code
        == HTTPStatus.UNAUTHORIZED
    )


def test_create_recipe(client, auth_headers):
    response = client.post('/recipes', json=PAYLOAD, headers=auth_headers)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, **PAYLOAD}


def test_create_recipe_accepts_empty_nome_refeicao(client, auth_headers):
    payload = {**PAYLOAD, 'nome_refeicao': ''}

    response = client.post('/recipes', json=payload, headers=auth_headers)

    assert response.status_code == HTTPStatus.CREATED


def test_create_recipe_validates_payload(client, auth_headers):
    bad_quantity = client.post(
        '/recipes',
        json={**PAYLOAD, 'quantidade': 'muito'},
        headers=auth_headers,
    )
    negative_kcal = client.post(
        '/recipes', json={**PAYLOAD, 'kcal': -1}, headers=auth_headers
    )
    missing = client.post(
        '/recipes', json={'nome_alimento': 'x'}, headers=auth_headers
    )

    assert bad_quantity.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert negative_kcal.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert missing.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_read_recipes_returns_recipes_key(client, recipe, auth_headers):
    response = client.get('/recipes', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert list(body) == ['recipes']
    assert body['recipes'][0]['id'] == recipe.id
    assert body['recipes'][0]['nome_alimento'] == 'Abobrinha Recheada'


def test_read_recipes_empty(client, auth_headers):
    response = client.get('/recipes', headers=auth_headers)

    assert response.json() == {'recipes': []}


def test_read_recipe(client, recipe, auth_headers):
    response = client.get(f'/recipes/{recipe.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': recipe.id,
        'nome_refeicao': 'Almoço',
        'nome_alimento': 'Abobrinha Recheada',
        'nome_categoria': 'Pratos Únicos',
        'quantidade': '250g',
        'kcal': 300,
        'dia_semana': 'Domingo',
    }


def test_read_recipe_not_found(client, auth_headers):
    response = client.get('/recipes/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}


def test_update_recipe(client, recipe, auth_headers):
    response = client.put(
        f'/recipes/{recipe.id}', json=PAYLOAD, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': recipe.id, **PAYLOAD}


def test_update_recipe_not_found(client, auth_headers):
    response = client.put('/recipes/999', json=PAYLOAD, headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_recipe(client, recipe, auth_headers):
    response = client.delete(f'/recipes/{recipe.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Recipe deleted'}
    after = client.get(f'/recipes/{recipe.id}', headers=auth_headers)
    assert after.status_code == HTTPStatus.NOT_FOUND


def test_delete_recipe_not_found(client, auth_headers):
    response = client.delete('/recipes/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_recipe_in_use_is_conflict(
    client, session, user, recipe, auth_headers
):
    session.add(
        ConsumptionLog(
            user_id=user.id,
            recipe_id=recipe.id,
            kcal=300,
            tipo_refeicao='almoço',
        )
    )
    session.commit()

    response = client.delete(f'/recipes/{recipe.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Recipe is used by records'}

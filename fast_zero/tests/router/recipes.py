from http import HTTPStatus


def test_create_recipe(client):
    response = client.post(
        '/recipes/',
        json={
            'id': 1,
            'nome_refeicao': 'breakfast',
            'nome_alimento': 'ovos',
            'nome_categoria': 'proteina',
            'quantidade': '2',
            'kcal': 200,
            'dia_semana': 'segunda',
            'message': 'delicious',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'nome_refeicao': 'breakfast',
        'nome_alimento': 'ovos',
        'nome_categoria': 'proteina',
        'quantidade': '2',
        'kcal': 200,
        'dia_semana': 'segunda',
        'message': 'delicious',
    }


def test_create_recipe_should_return_409_idrecipe_exists(client, recipe):
    response = client.post(
        '/recipes/',
        json={
            'id': 1,
            'nome_refeicao': 'breakfast',
            'nome_alimento': 'ovos',
            'nome_categoria': 'proteina',
            'quantidade': '2',
            'kcal': 200,
            'dia_semana': 'segunda',
            'message': 'delicious',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'ID Alimento already exists'}


def test_get_recipe___exercicio(client, recipe):
    response = client.get(f'/recipes/{recipe.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': recipe.id,
        'nome_refeicao': recipe.nome_refeicao,
        'nome_alimento': recipe.nome_alimento,
        'nome_categoria': recipe.nome_categoria,
        'quantidade': recipe.quantidade,
        'kcal': recipe.kcal,
        'dia_semana': recipe.dia_semana,
        'message': recipe.message,
    }


def test_read_recipes(client):
    response = client.get('/recipes/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'recipes': [
            {
                'id': 1,
                'nome_refeicao': 'breakfast',
                'nome_alimento': 'ovos',
                'nome_categoria': 'proteina',
                'quantidade': '2',
                'kcal': 200,
                'dia_semana': 'segunda',
                'message': 'delicious',
            }
        ]
    }


def test_update_recipe(client):
    response = client.put(
        '/recipes/1',
        json={
            'id': 1,
            'nome_refeicao': 'breakfast',
            'nome_alimento': 'ovos',
            'nome_categoria': 'proteina',
            'quantidade': '2',
            'kcal': 200,
            'dia_semana': 'segunda',
            'message': 'delicious',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'nome_refeicao': 'breakfast',
        'nome_alimento': 'ovos',
        'nome_categoria': 'proteina',
        'quantidade': '2',
        'kcal': 200,
        'dia_semana': 'segunda',
        'message': 'delicious',
    }


def test_delete_recipe(client):
    response = client.delete('/recipes/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'recipe deleted'}

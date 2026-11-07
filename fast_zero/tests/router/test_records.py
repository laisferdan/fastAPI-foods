from http import HTTPStatus

import pytest

from fast_zero.models.models import RecipeModel

DATE = '2026-11-07'


def _payload(recipe, **overrides):
    payload = {
        'data': DATE,
        'tipo_refeicao': 'almoço',
        'recipe_id': recipe.id,
        'quantidade_g': 250,
    }
    payload.update(overrides)
    return payload


def _create(client, headers, recipe, **overrides):
    response = client.post(
        '/records', json=_payload(recipe, **overrides), headers=headers
    )
    assert response.status_code == HTTPStatus.CREATED, response.text
    return response.json()


def test_records_require_token(client, recipe):
    assert (
        client.get('/records', params={'date': DATE}).status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert (
        client.post('/records', json=_payload(recipe)).status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert (
        client.put('/records/1', json=_payload(recipe)).status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert client.delete('/records/1').status_code == HTTPStatus.UNAUTHORIZED


def test_create_record_calculates_kcal(client, recipe, auth_headers):
    body = _create(client, auth_headers, recipe)

    assert body == {
        'id': 1,
        'data': DATE,
        'tipo_refeicao': 'almoço',
        'recipe_id': recipe.id,
        'quantidade_g': 250,
        'kcal': 300,
        'nome_alimento': 'Abobrinha Recheada',
        'nome_categoria': 'Pratos Únicos',
    }


@pytest.mark.parametrize(
    ('grams', 'expected'), [(125, 150), (500, 600), (100, 120)]
)
def test_kcal_is_proportional_to_grams(
    client, recipe, auth_headers, grams, expected
):
    body = _create(client, auth_headers, recipe, quantidade_g=grams)

    assert body['kcal'] == expected


def test_kcal_rounds_fractional_recipe_values(client, session, auth_headers):
    cafe = RecipeModel(
        nome_refeicao='Café da manhã',
        nome_alimento='Café',
        nome_categoria='Bebidas',
        quantidade='10g',
        kcal=35.3,
        dia_semana='Domingo',
    )
    session.add(cafe)
    session.commit()

    body = _create(
        client,
        auth_headers,
        cafe,
        tipo_refeicao='cafe_da_manha',
        quantidade_g=10,
    )

    assert body['kcal'] == 35


@pytest.mark.parametrize(
    'overrides',
    [
        {'tipo_refeicao': 'lanche'},
        {'quantidade_g': 0},
        {'quantidade_g': -5},
        {'recipe_id': 0},
        {'data': 'ontem'},
    ],
)
def test_create_record_validation(client, recipe, auth_headers, overrides):
    response = client.post(
        '/records',
        json=_payload(recipe, **overrides),
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_record_unknown_recipe(client, recipe, auth_headers):
    response = client.post(
        '/records',
        json=_payload(recipe, recipe_id=999),
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}


def test_list_records_by_date(client, recipe, auth_headers):
    _create(client, auth_headers, recipe)
    _create(client, auth_headers, recipe, tipo_refeicao='jantar')
    _create(client, auth_headers, recipe, data='2026-11-08')

    response = client.get(
        '/records', params={'date': DATE}, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    records = response.json()['records']
    assert [r['tipo_refeicao'] for r in records] == ['almoço', 'jantar']
    assert {r['data'] for r in records} == {DATE}


def test_list_records_empty_day(client, auth_headers):
    response = client.get(
        '/records', params={'date': DATE}, headers=auth_headers
    )

    assert response.json() == {'records': []}


def test_list_records_requires_valid_date(client, auth_headers):
    missing = client.get('/records', headers=auth_headers)
    invalid = client.get(
        '/records', params={'date': '2026-13-45'}, headers=auth_headers
    )

    assert missing.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_record_recalculates(client, recipe, auth_headers):
    created = _create(client, auth_headers, recipe)

    response = client.put(
        f'/records/{created["id"]}',
        json=_payload(
            recipe,
            quantidade_g=125,
            tipo_refeicao='jantar',
            data='2026-11-09',
        ),
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['kcal'] == 150
    assert body['tipo_refeicao'] == 'jantar'
    assert body['data'] == '2026-11-09'
    old_day = client.get(
        '/records', params={'date': DATE}, headers=auth_headers
    )
    assert old_day.json() == {'records': []}


def test_update_record_not_found_and_unknown_recipe(
    client, recipe, auth_headers
):
    missing = client.put(
        '/records/999', json=_payload(recipe), headers=auth_headers
    )
    created = _create(client, auth_headers, recipe)
    bad_recipe = client.put(
        f'/records/{created["id"]}',
        json=_payload(recipe, recipe_id=999),
        headers=auth_headers,
    )

    assert missing.status_code == HTTPStatus.NOT_FOUND
    assert bad_recipe.status_code == HTTPStatus.NOT_FOUND
    assert bad_recipe.json() == {'detail': 'Recipe not found'}


def test_delete_record(client, recipe, auth_headers):
    created = _create(client, auth_headers, recipe)

    response = client.delete(f'/records/{created["id"]}', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Record deleted'}
    listing = client.get(
        '/records', params={'date': DATE}, headers=auth_headers
    )
    assert listing.json() == {'records': []}
    again = client.delete(f'/records/{created["id"]}', headers=auth_headers)
    assert again.status_code == HTTPStatus.NOT_FOUND


def test_user_cannot_see_edit_or_delete_another_users_record(
    client, recipe, auth_headers, other_auth_headers
):
    mine = _create(client, auth_headers, recipe)

    listing = client.get(
        '/records', params={'date': DATE}, headers=other_auth_headers
    )
    put = client.put(
        f'/records/{mine["id"]}',
        json=_payload(recipe, quantidade_g=1),
        headers=other_auth_headers,
    )
    delete = client.delete(
        f'/records/{mine["id"]}', headers=other_auth_headers
    )

    assert listing.json() == {'records': []}
    assert put.status_code == HTTPStatus.NOT_FOUND
    assert delete.status_code == HTTPStatus.NOT_FOUND
    still_there = client.get(
        '/records', params={'date': DATE}, headers=auth_headers
    )
    assert still_there.json()['records'][0]['quantidade_g'] == 250


def test_records_feed_analytics(client, recipe, auth_headers):
    _create(client, auth_headers, recipe, data='2026-11-07')

    response = client.get(
        '/analytics/me/summary',
        params={
            'start_date': '2026-11-07T00:00:00',
            'end_date': '2026-11-07T23:59:59',
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['total_kcal'] == 300

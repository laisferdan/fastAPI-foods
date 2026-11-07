from sqlalchemy import func, select

from fast_zero.models.models import RecipeModel
from fast_zero.security.passwords import get_password_hash, verify_password
from fast_zero.seeds.recipes import load_seed_data, seed_recipes


def test_seed_inserts_all_recipes_with_original_ids(session):
    created = seed_recipes(session)

    assert created == 11
    ids = session.scalars(select(RecipeModel.id).order_by(RecipeModel.id))
    assert ids.all() == list(range(1, 12))


def test_seed_preserves_source_values(session):
    seed_recipes(session)

    cafe = session.get(RecipeModel, 11)
    assert (cafe.nome_alimento, cafe.kcal, cafe.nome_refeicao) == (
        'Café',
        35.3,
        'Café da manhã',
    )
    assert not session.get(RecipeModel, 7).nome_refeicao


def test_seed_is_idempotent_and_does_not_overwrite(session):
    seed_recipes(session)
    edited = session.get(RecipeModel, 1)
    edited.kcal = 999
    session.commit()

    created_again = seed_recipes(session)

    assert created_again == 0
    assert session.scalar(select(func.count(RecipeModel.id))) == 11
    assert session.get(RecipeModel, 1).kcal == 999


def test_seed_data_file_has_expected_shape():
    items = load_seed_data()

    assert len(items) == 11
    assert all('codigo' not in item for item in items)


def test_password_hash_roundtrip():
    hashed = get_password_hash('my-password')

    assert hashed != 'my-password'
    assert verify_password('my-password', hashed)
    assert not verify_password('other', hashed)

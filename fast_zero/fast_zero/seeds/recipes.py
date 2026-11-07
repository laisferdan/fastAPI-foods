"""Seed idempotente da tabela recipes.

Uso: ``python -m fast_zero.seeds.recipes`` (ou ``task seed``).
Insere somente os pratos cujo id ainda não existe; nunca sobrescreve.
"""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from fast_zero.database.database import engine
from fast_zero.models.models import RecipeModel

SEED_FILE = Path(__file__).with_name('recipes.json')


def load_seed_data(path: Path = SEED_FILE) -> list[dict]:
    with path.open(encoding='utf-8') as file:
        return json.load(file)['recipes']


def seed_recipes(session: Session, items: list[dict] | None = None) -> int:
    """Insere os pratos ausentes e devolve quantos foram criados."""
    items = load_seed_data() if items is None else items
    created = 0
    for item in items:
        if session.get(RecipeModel, item['id']) is not None:
            continue
        recipe = RecipeModel(
            nome_refeicao=item['nome_refeicao'],
            nome_alimento=item['nome_alimento'],
            nome_categoria=item['nome_categoria'],
            quantidade=item['quantidade'],
            kcal=item['kcal'],
            dia_semana=item['dia_semana'],
        )
        recipe.id = item['id']
        session.add(recipe)
        created += 1
    session.commit()
    return created


def main() -> None:  # pragma: no cover
    with Session(engine) as session:
        created = seed_recipes(session)
    print(f'recipes: {created} criada(s), restante já existia.')


if __name__ == '__main__':  # pragma: no cover
    main()

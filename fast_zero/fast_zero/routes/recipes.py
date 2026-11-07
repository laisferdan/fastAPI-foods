from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import ConsumptionLog, RecipeModel
from fast_zero.schemas.recipes import (
    RecipeCreate,
    RecipeList,
    RecipePublic,
)
from fast_zero.schemas.users import Message
from fast_zero.security.auth import get_current_user_id

router = APIRouter(
    prefix='/recipes',
    tags=['recipes'],
    dependencies=[Depends(get_current_user_id)],
)

DbSession = Annotated[Session, Depends(get_session)]


def _get_or_404(session: Session, recipe_id: int) -> RecipeModel:
    recipe = session.get(RecipeModel, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Recipe not found'
        )
    return recipe


@router.get('', response_model=RecipeList)
def read_recipes(session: DbSession):
    recipes = session.scalars(select(RecipeModel).order_by(RecipeModel.id))
    return {'recipes': recipes.all()}


@router.get('/{recipe_id}', response_model=RecipePublic)
def read_recipe(recipe_id: int, session: DbSession):
    return _get_or_404(session, recipe_id)


@router.post('', status_code=HTTPStatus.CREATED, response_model=RecipePublic)
def create_recipe(recipe: RecipeCreate, session: DbSession):
    db_recipe = RecipeModel(**recipe.model_dump())
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


@router.put('/{recipe_id}', response_model=RecipePublic)
def update_recipe(recipe_id: int, recipe: RecipeCreate, session: DbSession):
    db_recipe = _get_or_404(session, recipe_id)
    for key, value in recipe.model_dump().items():
        setattr(db_recipe, key, value)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


@router.delete('/{recipe_id}', response_model=Message)
def delete_recipe(recipe_id: int, session: DbSession):
    db_recipe = _get_or_404(session, recipe_id)
    in_use = session.scalar(
        select(ConsumptionLog.id)
        .where(ConsumptionLog.recipe_id == recipe_id)
        .limit(1)
    )
    if in_use is not None:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Recipe is used by records',
        )
    session.delete(db_recipe)
    session.commit()
    return {'message': 'Recipe deleted'}

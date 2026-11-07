import re
from datetime import date, datetime, time, timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.models.models import ConsumptionLog, RecipeModel, User
from fast_zero.schemas.records import (
    RecordCreate,
    RecordList,
    RecordPublic,
)
from fast_zero.schemas.users import Message
from fast_zero.security.auth import get_current_user

router = APIRouter(prefix='/records', tags=['records'])

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

_BASE_GRAMS = re.compile(r'^(\d+(?:\.\d+)?)g$')


def _calc_kcal(recipe: RecipeModel, quantidade_g: float) -> int:
    match = _BASE_GRAMS.match(recipe.quantidade.strip())
    base_g = float(match.group(1)) if match else 0.0
    if base_g <= 0:
        return round(recipe.kcal)
    return round(recipe.kcal * quantidade_g / base_g)


def _to_public(log: ConsumptionLog, recipe: RecipeModel) -> RecordPublic:
    return RecordPublic(
        id=log.id,
        data=log.consumed_at.date(),
        tipo_refeicao=log.tipo_refeicao,
        recipe_id=log.recipe_id,
        quantidade_g=log.quantidade_g,
        kcal=log.kcal,
        nome_alimento=recipe.nome_alimento,
        nome_categoria=recipe.nome_categoria,
    )


def _get_recipe_or_404(session: Session, recipe_id: int) -> RecipeModel:
    recipe = session.get(RecipeModel, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Recipe not found'
        )
    return recipe


def _get_own_log_or_404(
    session: Session, record_id: int, user: User
) -> ConsumptionLog:
    log = session.scalar(
        select(ConsumptionLog).where(
            ConsumptionLog.id == record_id,
            ConsumptionLog.user_id == user.id,
        )
    )
    if log is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Record not found'
        )
    return log


@router.get('', response_model=RecordList)
def read_records(
    current_user: CurrentUser,
    session: DbSession,
    date_: Annotated[date, Query(alias='date')],
):
    start = datetime.combine(date_, time.min)
    end = start + timedelta(days=1)
    rows = session.execute(
        select(ConsumptionLog, RecipeModel)
        .join(RecipeModel, RecipeModel.id == ConsumptionLog.recipe_id)
        .where(
            ConsumptionLog.user_id == current_user.id,
            ConsumptionLog.consumed_at >= start,
            ConsumptionLog.consumed_at < end,
        )
        .order_by(ConsumptionLog.id)
    ).all()
    return {'records': [_to_public(log, recipe) for log, recipe in rows]}


@router.post('', status_code=HTTPStatus.CREATED, response_model=RecordPublic)
def create_record(
    record: RecordCreate, current_user: CurrentUser, session: DbSession
):
    recipe = _get_recipe_or_404(session, record.recipe_id)
    log = ConsumptionLog(
        user_id=current_user.id,
        recipe_id=recipe.id,
        kcal=_calc_kcal(recipe, record.quantidade_g),
        tipo_refeicao=record.tipo_refeicao.value,
        consumed_at=datetime.combine(record.data, time.min),
        quantidade_g=record.quantidade_g,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return _to_public(log, recipe)


@router.put('/{record_id}', response_model=RecordPublic)
def update_record(
    record_id: int,
    record: RecordCreate,
    current_user: CurrentUser,
    session: DbSession,
):
    log = _get_own_log_or_404(session, record_id, current_user)
    recipe = _get_recipe_or_404(session, record.recipe_id)
    log.recipe_id = recipe.id
    log.kcal = _calc_kcal(recipe, record.quantidade_g)
    log.tipo_refeicao = record.tipo_refeicao.value
    log.consumed_at = datetime.combine(record.data, time.min)
    log.quantidade_g = record.quantidade_g
    session.commit()
    session.refresh(log)
    return _to_public(log, recipe)


@router.delete('/{record_id}', response_model=Message)
def delete_record(
    record_id: int, current_user: CurrentUser, session: DbSession
):
    log = _get_own_log_or_404(session, record_id, current_user)
    session.delete(log)
    session.commit()
    return {'message': 'Record deleted'}

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fast_zero.database.database import get_session
from fast_zero.repositories.analytics import (
    get_calories_by_day,
    get_distribution_by_meal,
    get_summary,
)
from fast_zero.schemas.analytics import (
    AnalyticsParams,
    CaloriesByDayOut,
    DistributionByMealOut,
    DistributionItem,
    SeriesPoint,
    SummaryOut,
)
from fast_zero.security.auth import get_current_user_id

router = APIRouter(prefix="/analytics/me", tags=["analytics"]) 


@router.get(
    "/summary",
    response_model=SummaryOut,
    summary="Resumo de consumo no período",
    description="Retorna total de calorias, número de refeições e total de alimentos do usuário no intervalo informado.",
)
def summary(
    params: AnalyticsParams = Depends(),
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    total_kcal, total_meals, total_foods = get_summary(
        session, user_id, params.start_date, params.end_date
    )
    return SummaryOut(total_kcal=total_kcal, total_meals=total_meals, total_foods=total_foods)


@router.get(
    "/calories-by-day",
    response_model=CaloriesByDayOut,
    summary="Série diária de calorias",
    description="Retorna pontos de calorias por dia dentro do período.",
)
def calories_by_day(
    params: AnalyticsParams = Depends(),
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    rows = get_calories_by_day(session, user_id, params.start_date, params.end_date)
    points = [SeriesPoint(date=dt, kcal=kcal) for dt, kcal in rows]
    return CaloriesByDayOut(points=points, total_days=len(points))


@router.get(
    "/distribution-by-meal",
    response_model=DistributionByMealOut,
    summary="Distribuição por tipo de refeição",
    description="Retorna kcal e percentual por tipo de refeição no período.",
)
def distribution_by_meal(
    params: AnalyticsParams = Depends(),
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    rows = get_distribution_by_meal(session, user_id, params.start_date, params.end_date)
    items = [DistributionItem(tipo_refeicao=kind, kcal=kcal, percent=pct) for kind, kcal, pct in rows]
    return DistributionByMealOut(items=items)

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from fast_zero.models.models import ConsumptionLog


def _between_clause(start: datetime, end: datetime):
    return (ConsumptionLog.consumed_at >= start) & (ConsumptionLog.consumed_at <= end)


def get_summary(session: Session, user_id: int, start: datetime, end: datetime) -> Tuple[int, int, int]:
    total_kcal_stmt: Select = select(func.coalesce(func.sum(ConsumptionLog.kcal), 0)).where(
        (ConsumptionLog.user_id == user_id) & _between_clause(start, end)
    )
    total_meals_stmt: Select = select(func.count()).where(
        (ConsumptionLog.user_id == user_id) & _between_clause(start, end)
    )

    total_kcal = session.scalar(total_kcal_stmt) or 0
    total_meals = session.scalar(total_meals_stmt) or 0

    total_foods = total_meals

    return int(total_kcal), int(total_meals), int(total_foods)


def get_calories_by_day(
    session: Session, user_id: int, start: datetime, end: datetime
) -> List[Tuple[datetime, int]]:
    stmt: Select = (
        select(func.date(ConsumptionLog.consumed_at), func.coalesce(func.sum(ConsumptionLog.kcal), 0))
        .where((ConsumptionLog.user_id == user_id) & _between_clause(start, end))
        .group_by(func.date(ConsumptionLog.consumed_at))
        .order_by(func.date(ConsumptionLog.consumed_at))
    )

    rows = session.execute(stmt).all()

    points: List[Tuple[datetime, int]] = []
    for day_str, kcal in rows:
        dt = datetime.fromisoformat(str(day_str)).replace(tzinfo=timezone.utc)
        points.append((dt, int(kcal)))

    return points


def get_distribution_by_meal(
    session: Session, user_id: int, start: datetime, end: datetime
) -> List[Tuple[str, int, float]]:
    per_meal_stmt: Select = (
        select(ConsumptionLog.tipo_refeicao, func.coalesce(func.sum(ConsumptionLog.kcal), 0))
        .where((ConsumptionLog.user_id == user_id) & _between_clause(start, end))
        .group_by(ConsumptionLog.tipo_refeicao)
        .order_by(ConsumptionLog.tipo_refeicao)
    )
    total_stmt: Select = select(func.coalesce(func.sum(ConsumptionLog.kcal), 0)).where(
        (ConsumptionLog.user_id == user_id) & _between_clause(start, end)
    )

    rows = session.execute(per_meal_stmt).all()
    total_kcal = session.scalar(total_stmt) or 0

    items: List[Tuple[str, int, float]] = []
    if total_kcal == 0:
        for meal, kcal in rows:
            items.append((meal, int(kcal), 0.0))
        return items

    total_kcal = float(total_kcal)
    for meal, kcal in rows:
        kcal_int = int(kcal)
        percent = round((kcal_int / total_kcal) * 100.0, 2)
        items.append((meal, kcal_int, percent))

    return items

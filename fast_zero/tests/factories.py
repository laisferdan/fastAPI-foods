from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from fast_zero.models.models import ConsumptionLog


def dt_midnight_utc(days_offset: int = 0) -> datetime:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=days_offset)


def make_consumption(
    session: Session,
    *,
    user_id: int,
    recipe_id: int,
    kcal: int,
    tipo_refeicao: str,
    consumed_at: datetime,
) -> ConsumptionLog:
    obj = ConsumptionLog(
        user_id=user_id,
        recipe_id=recipe_id,
        kcal=kcal,
        tipo_refeicao=tipo_refeicao,
        consumed_at=consumed_at,
    )
    session.add(obj)
    return obj


def bulk_make_consumptions(
    session: Session,
    items: Iterable[tuple[int, int, int, str, datetime]],
) -> None:
    for user_id, recipe_id, kcal, tipo, ts in items:
        session.add(
            ConsumptionLog(
                user_id=user_id,
                recipe_id=recipe_id,
                kcal=kcal,
                tipo_refeicao=tipo,
                consumed_at=ts,
            )
        )
    session.commit()

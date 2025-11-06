from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from fast_zero.models.models import ConsumptionLog, RecommendationFeedback, RecipeModel


def kcal_consumed_on(session: Session, user_id: int, on_date: date) -> int:
    start = datetime.combine(on_date, datetime.min.time())
    end = datetime.combine(on_date, datetime.max.time())
    total = session.scalar(
        select(func.coalesce(func.sum(ConsumptionLog.kcal), 0)).where(
            and_(
                ConsumptionLog.user_id == user_id,
                ConsumptionLog.consumed_at >= start,
                ConsumptionLog.consumed_at <= end,
            )
        )
    )
    return int(total or 0)


def recent_categories(session: Session, user_id: int, limit: int = 10) -> list[str]:
    rows = session.execute(
        select(RecipeModel.nome_categoria)
        .join(ConsumptionLog, ConsumptionLog.recipe_id == RecipeModel.id)
        .where(ConsumptionLog.user_id == user_id)
        .order_by(ConsumptionLog.consumed_at.desc())
        .limit(limit)
    ).all()
    return [r[0] for r in rows]


def user_feedback_map(session: Session, user_id: int) -> dict[int, str]:
    rows = session.execute(
        select(RecommendationFeedback.recipe_id, RecommendationFeedback.feedback).where(
            RecommendationFeedback.user_id == user_id
        )
    ).all()
    return {rid: fb for rid, fb in rows}

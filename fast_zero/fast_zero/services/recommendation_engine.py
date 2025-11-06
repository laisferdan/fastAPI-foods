from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models.models import RecommendationFeedback, RecipeModel, UserProfile
from fast_zero.repositories.recommendation import (
    kcal_consumed_on,
    recent_categories,
    user_feedback_map,
)
from fast_zero.services.tdee import Profile, tdee
from fast_zero.services.embeddings import kcal_vector2d, cosine_similarity
from loguru import logger


@dataclass
class Recommendation:
    recipe_id: int
    nome_refeicao: str
    kcal: int
    tipo: str
    adequacao_percentual: float


def _adequacao_percentual(kcal_restante: float, kcal_item: int) -> float:
    if kcal_restante <= 0:
        return 0.0
    diff = abs(kcal_restante - kcal_item)
    perc = max(0.0, 1.0 - (diff / kcal_restante)) * 100.0
    return round(perc, 2)


def recommend_for_user(session: Session, user_id: int, on_date: date, top_n: int = 5) -> list[Recommendation]:
    prof = session.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if not prof:
        return []

    p = Profile(
        sexo=prof.sexo,
        idade=prof.idade,
        peso_kg=prof.peso_kg,
        altura_cm=prof.altura_cm,
        nivel_atividade=prof.nivel_atividade,
    )
    meta_diaria = tdee(p)
    consumido = kcal_consumed_on(session, user_id, on_date)
    restante = max(0.0, meta_diaria - consumido)
    logger.debug(
        "Reco context user_id={}, date={}, tdee={}, consumed={}, remaining={}",
        user_id,
        on_date,
        round(meta_diaria, 2),
        consumido,
        round(restante, 2),
    )

    low = max(0.0, restante * 0.9)
    high = restante * 1.1

    rows = session.execute(select(RecipeModel)).scalars().all()
    if not rows:
        return []

    cats = recent_categories(session, user_id)
    fb = user_feedback_map(session, user_id)

    min_kcal = min(r.kcal for r in rows)
    max_kcal = max(r.kcal for r in rows)
    v_target = kcal_vector2d(restante, min_kcal, max_kcal)

    def score(recipe: RecipeModel) -> float:
        if not (low <= recipe.kcal <= high):
            return -1.0
        base = _adequacao_percentual(restante, recipe.kcal)
        v_item = kcal_vector2d(recipe.kcal, min_kcal, max_kcal)
        sim = cosine_similarity(v_target, v_item)
        base += sim * 10.0  # peso leve, ajustável
        if recipe.nome_categoria in cats:
            base += 5.0
        if fb.get(recipe.id) == 'dislike':
            base -= 10.0
        elif fb.get(recipe.id) == 'like':
            base += 2.5
        return base

    scored = []
    for r in rows:
        s = score(r)
        if s >= 0:
            scored.append(
                (
                    s,
                    Recommendation(
                        recipe_id=r.id,
                        nome_refeicao=r.nome_refeicao,
                        kcal=r.kcal,
                        tipo=r.nome_refeicao,
                        adequacao_percentual=_adequacao_percentual(restante, r.kcal),
                    ),
                )
            )

    scored.sort(key=lambda x: x[0], reverse=True)
    return [rec for _, rec in scored[:top_n]]
